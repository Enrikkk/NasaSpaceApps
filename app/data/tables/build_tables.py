#!/usr/bin/env python3
"""Build T-021 tables from Enrique's official-data snapshot, without imputing gaps."""
import argparse
import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

CROPS = ('lechuga', 'brocoli', 'melon', 'alcachofa', 'haba', 'cebada', 'veza', 'limon')
REQUIRED = ('family', 'legal_group', 'kc_ini', 'kc_mid', 'kc_end', 'stages_days',
            'root_depth', 'ece_threshold', 'ece_slope', 'frost_threshold', 'heat_threshold',
            'produccion_media', 'n_need', 'n_credit', 'legume')
META = ('unit', 'source_id', 'conf', 'status', 'nota')


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def write(path, rows, fields):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def build(source, dest, revision):
    dest.mkdir(parents=True, exist_ok=True)
    source_rows = read(source / 'sources.csv')
    sources = {r['source_id']: r for r in source_rows}
    if len(sources) != len(source_rows):
        raise ValueError('Duplicate source ID')
    params = read(source / 'fao_crop_params.csv') + read(source / 'imida_costs.csv')
    indexed = {}
    for row in params:
        key = row['crop_id'], row['param']
        if key in indexed or key[0] not in CROPS:
            raise ValueError(f'Duplicate/unknown crop parameter: {key}')
        placeholder = row['value'] == '' and row['conf'] == 'P' and row['status'] == 'placeholder'
        if (row['source_id'] not in sources and not placeholder) or row['conf'] not in ('A', 'M', 'B', 'P'):
            raise ValueError(f'Invalid provenance: {key}')
        indexed[key] = dict(row)
    required = set(REQUIRED) | {r['param'] for r in params}
    missing = []
    for crop in CROPS:
        for param in sorted(required):
            if (crop, param) not in indexed:
                # Do not invent per-crop values or turn missing costs into zero.
                row = dict(crop_id=crop, param=param, value='', unit='', source_id='',
                           conf='P', status='placeholder', nota='No verified value in source snapshot')
                indexed[crop, param] = row
            if indexed[crop, param]['value'] == '' and (param in REQUIRED or param == 'coste_total'):
                missing.append({'crop_id': crop, 'param': param})
    long_rows = [indexed[crop, param] for crop in CROPS for param in sorted(required)]
    write(dest / 'crop_params.csv', long_rows,
          ['crop_id', 'param', 'value', *META])
    wide = []
    wide_fields = ['crop_id']
    for param in sorted(required):
        wide_fields.extend([param, *(param + '__' + ('note' if field == 'nota' else field) for field in META)])
    for crop in CROPS:
        row = {'crop_id': crop}
        for param in sorted(required):
            cell = indexed[crop, param]
            row[param] = cell['value']
            row.update({param + '__' + ('note' if field == 'nota' else field): cell[field] for field in META})
        wide.append(row)
    write(dest / 'crops.csv', wide, wide_fields)
    costs = read(source / 'imida_costs.csv')
    cost_params = sorted({r['param'] for r in costs})
    costs = [dict(indexed[crop, param], source_year='',
                  price_base_year='2018' if indexed[crop, param]['value'] and 'EUR' in indexed[crop, param]['unit'] else '',
                  monetary_basis='historical_nominal_unadjusted',
                  basis_note='IMIDA base 2018 per Enrique #54 (survey 2017-19); no inflation adjustment')
             for crop in CROPS for param in cost_params]
    write(dest / 'costs.csv', costs,
          ['crop_id', 'param', 'value', *META, 'source_year', 'price_base_year', 'monetary_basis', 'basis_note'])
    prices = []
    seen = set()
    for original in read(source / 'eurostat_prices_es.csv'):
        row = dict(original)
        key = row['crop_id'], row['year']
        if key in seen or row['crop_id'] not in CROPS:
            raise ValueError(f'Duplicate/unknown price: {key}')
        seen.add(key)
        for old, new in [('eur_100kg', 'eur_kg'), ('eur_100kg_real2015', 'eur_kg_real2015')]:
            row[new] = str(Decimal(row[old]) / 100) if row[old] else ''
        row.update(source_id='EUR-PRICE', deflator_source_id='EUR-HICP',
                   conf='M' if row['crop_id'] == 'brocoli' else 'A',
                   status='proxy' if row['crop_id'] == 'brocoli' else 'sourced',
                   nota='Cauliflower price used for broccoli' if row['crop_id'] == 'brocoli' else '')
        prices.append(row)
    if prices:
        write(dest / 'prices.csv', prices, list(prices[0]))
    area = read(source / 'eurostat_area_es.csv')
    write(dest / 'area.csv', area, list(area[0]))
    write(dest / 'sources.csv', source_rows, list(source_rows[0]))
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(source.glob('*.csv'))}
    manifest = {'source_revision': revision, 'input_sha256': hashes,
                'crops': list(CROPS), 'source_parameter_rows': len(params),
                'prices': len(prices), 'missing_required_values': missing,
                'price_missing_crops': [c for c in CROPS if c not in {r['crop_id'] for r in prices}],
                'limitations': ['National annual prices are not local farm forecasts.',
                                'No inflation alignment: real2015 prices must not be mixed with historical nominal costs.',
                                'Cover vetch is not harvested forage: forage costs require an explicit proxy decision.',
                                'No missing value has been replaced by zero.'],
                'license_review': {k: 'pending_review' for k in sources
                                   if k.startswith(('F56', 'F29', 'IMIDA', 'RES'))}}
    (dest / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--revision', required=True)
    args = ap.parse_args()
    result = build(args.input, args.output, args.revision)
    print(json.dumps({k: result[k] for k in ('source_revision', 'source_parameter_rows', 'prices')}))
