#!/usr/bin/env python3
"""Extract MAPA's Anual column from downloaded XLSX files; never fetch or change engine defaults."""
import argparse
import csv
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
LABELS = {'LECHUGA': 'lechuga', 'MELON': 'melon', 'ALCACHOFA': 'alcachofa'}
YEARS = range(2005, 2025)
LEGAL = 'https://www.mapa.gob.es/es/atencion-al-ciudadano/aviso-legal'
LICENCE = 'MAPA legal notice: reuse with source attribution under Ley 37/2007; retain update/reuse metadata; third-party rights excluded; not a CC licence'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sheet_rows(path):
    with zipfile.ZipFile(path) as z:
        strings = [''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        sheets = ET.fromstring(z.read('xl/workbook.xml')).find('s:sheets', NS)
        sheet = next(e for e in sheets if e.get('name') == 'PrePer3')
        rels = {e.get('Id'): e.get('Target') for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        target = rels[sheet.get(RID)]
        target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        styles = ET.fromstring(z.read('xl/styles.xml')).find('s:cellXfs', NS)
        rows = []
        for row in ET.fromstring(z.read(target)).findall('s:sheetData/s:row', NS):
            cells = {}
            for c in row:
                ref = c.get('r')
                col = re.sub(r'\d+', '', ref)
                v = c.find('s:v', NS)
                value = '' if v is None else v.text
                if c.get('t') == 's':
                    value = strings[int(value)]
                elif c.get('t') == 'inlineStr':
                    value = ''.join(c.find('s:is', NS).itertext())
                cells[col] = {'value': value, 'cell': ref, 'format_id': styles[int(c.get('s', '0'))].get('numFmtId')}
            rows.append(cells)
        core = ET.fromstring(z.read('docProps/core.xml'))
        dates = {e.tag.rsplit('}', 1)[-1]: e.text for e in core if e.tag.rsplit('}', 1)[-1] in ('created', 'modified', 'lastPrinted')}
        # Keep source notes and update/reuse metadata; not just the selected numeric cells.
        notes = [e for row in rows for c in row.values() if (e := c['value']) and isinstance(e, str) and e.startswith('Nota')]
        return rows, dates, notes


def extract(path):
    rows, dates, notes = sheet_rows(path)
    annual = year_col = None
    crop = label = None
    found = {}
    for row in rows:
        for col, c in row.items():
            if c['value'] == 'Anual':
                annual = col
            if c['value'] == 'AÑO':
                year_col = col
        raw_label = row.get('A', {}).get('value', '')
        if raw_label and raw_label != '0':
            label = raw_label
            crop = next((c for name, c in LABELS.items() if re.match(name + r'\s*\(', label)), None)
            if crop and not re.search(r'100\s*KG', label, re.I):
                raise ValueError(f'Unexpected source unit: {label}')
        if crop is None or annual is None or year_col is None:
            continue
        year = row.get(year_col, {}).get('value', '')
        if not str(year).isdigit() or int(year) not in YEARS:
            continue
        cell = row.get(annual)
        if not cell or cell['value'] in ('', '-', None):
            continue
        value = Decimal(cell['value'])
        if not value.is_finite() or value <= 0 or cell['format_id'] != '2':
            raise ValueError(f'Invalid annual value/format: {path}/{cell}')
        # Built-in Excel numFmtId=2 is 0.00: preserve the published two-decimal display.
        value = value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        key = crop, int(year)
        if key in found:
            raise ValueError(f'Duplicate annual crop/year in workbook: {key}')
        found[key] = {'crop_id': crop, 'year': str(year), 'eur_100kg': str(value),
                      'source_cell': cell['cell'], 'source_raw_value': cell['value'], 'source_label': label}
    return found, dates, notes


def build(inputs, catalog_path, output, hicp_path):
    catalog = json.loads(catalog_path.read_text())
    with hicp_path.open() as f:
        hicp = {int(r['year']): Decimal(r['hicp_2015_100']) for r in csv.DictReader(f)}
    selected, workbooks, overlaps = {}, [], []
    for entry in catalog['workbooks']:
        path = inputs / entry['file']
        rows, dates, notes = extract(path)
        meta = dict(entry, sha256=digest(path), workbook_dates=dates, sheet='PrePer3', source_notes=notes)
        if workbooks and dates['modified'] <= workbooks[-1]['workbook_dates']['modified']:
            raise ValueError('Catalog must be ordered by increasing source modification date')
        workbooks.append(meta)
        for key, row in rows.items():
            if key in selected:
                old = selected[key]
                overlaps.append({'crop_id': key[0], 'year': key[1], 'previous_source': old['source_id'],
                                 'previous_value': old['eur_100kg'], 'selected_source': entry['source_id'],
                                 'selected_value': row['eur_100kg']})
            row.update(source_id=entry['source_id'], source_url=entry['url'],
                       source_updated_at=dates['modified'], source_sheet='PrePer3',
                       downloaded_at=catalog['downloaded_at'], source_sha256=meta['sha256'])
            selected[key] = row
    missing = [(c, y) for c in LABELS.values() for y in YEARS if (c, y) not in selected]
    if missing:
        raise ValueError(f'Missing annual prices (not imputed): {missing}')
    result = []
    for key in sorted(selected):
        r = selected[key]
        value, index = Decimal(r['eur_100kg']), hicp[int(r['year'])]
        if not index.is_finite() or index <= 0:
            raise ValueError('HICP must be finite and positive')
        real = (value * 100 / index).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        # Same leading columns as prices.csv; MAPA has no Eurostat code, so code stays empty.
        out = dict(crop_id=r['crop_id'], year=r['year'], eur_100kg=r['eur_100kg'],
                   eur_100kg_real2015=str(real), code='', eur_kg=str(value / 100),
                   eur_kg_real2015=str(real / 100), source_id=r['source_id'], deflator_source_id='EUR-HICP',
                   conf='B', status='proxy', nota='National generic crop annual price; not Murcia or a cultivar price; no piece-to-weight conversion; harvest cost inclusion not verified')
        out.update({k: v for k, v in r.items() if k not in out})
        out.update(unit='EUR/100 kg', monetary_basis='nominal_by_year; real2015 derived with Spain HICP',
                   source_period='Anual', legal_url=LEGAL, licence=LICENCE)
        result.append(out)
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'mapa_prices.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(result[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(result)
    manifest = dict(dataset='MAPA Indices y Precios Percibidos Agrarios, PrePer3 / Anual',
                    downloaded_at=catalog['downloaded_at'], years=[min(YEARS), max(YEARS)], rows=len(result),
                    selection='Latest workbook modification date wins for overlapping crop/year; never average overlapping editions.',
                    workbooks=workbooks, overlaps=overlaps, hicp_sha256=digest(hicp_path),
                    legal_url=LEGAL, licence=LICENCE, legal_html_sha256=digest(inputs / 'legal.html'),
                    output_sha256=digest(output / 'mapa_prices.csv'),
                    limitations=['Generic national crop proxy, not regional or cultivar-specific.',
                                 'No monthly average computed: source Anual column only.',
                                 'Years after 2024 excluded, including incomplete/provisional 2026.',
                                 'Horticulture source note: bulk price at buyer warehouse; harvest-cost treatment remains unknown.',
                                 'Eurostat/FAOSTAT may redistribute MAPA: not independent validation.',
                                 'No engine default changed; prices.csv left unchanged.'])
    (output / 'mapa_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--catalog', type=Path, default=Path(__file__).with_name('mapa_inputs.json'))
    ap.add_argument('--output', type=Path, default=Path(__file__).parent)
    ap.add_argument('--hicp', type=Path, default=Path(__file__).with_name('eurostat_hicp_es.csv'))
    args = ap.parse_args()
    m = build(args.input, args.catalog, args.output, args.hicp)
    print(json.dumps({'rows': m['rows'], 'years': m['years'], 'overlap_rows': len(m['overlaps'])}))
