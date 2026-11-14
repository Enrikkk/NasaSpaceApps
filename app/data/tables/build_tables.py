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
            'zr_min', 'zr_max', 'p_depletion', 'ece_threshold', 'ece_slope',
            'sowing_month', 'frost_t0', 'frost_t100', 'heat_t0', 'heat_t100',
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


def build(source, dest, revision, supplement=None):
    dest.mkdir(parents=True, exist_ok=True)
    source_rows = read(source / 'sources.csv')
    if supplement:
        source_rows += read(supplement / 'sources.csv')
    sources = {r['source_id']: r for r in source_rows}
    if len(sources) != len(source_rows):
        raise ValueError('Duplicate source ID')
    products = read(source / 'products.csv') if (source / 'products.csv').exists() else []
    product_ids = {r['product_id'] for r in products}
    if len(product_ids) != len(products) or any(r['crop_id'] not in CROPS for r in products):
        raise ValueError('Duplicate product or unknown base crop')
    if any(r.get('cost_product') and r['cost_product'] not in product_ids | set(CROPS) for r in products):
        raise ValueError('Unknown cost product')
    params = read(source / 'fao_crop_params.csv') + read(source / 'imida_costs.csv')
    if supplement:
        params += read(supplement / 'crop_params.csv')
    indexed = {}
    for row in params:
        key = row['crop_id'], row['param']
        if key in indexed or key[0] not in set(CROPS) | product_ids:
            raise ValueError(f'Duplicate/unknown crop parameter: {key}')
        placeholder = row['value'] == '' and row['conf'] == 'P' and row['status'] == 'placeholder'
        refs = row['source_id'].split('+')
        if (any(ref not in sources for ref in refs) and not placeholder) or row['conf'] not in ('A', 'M', 'B', 'P'):
            raise ValueError(f'Invalid provenance: {key}')
        if row['param'] in ('frost_threshold', 'heat_threshold'):
            raise ValueError(f'Obsolete threshold name: {key}')
        if row['value'] and row['param'] in ('frost_t0', 'frost_t100', 'heat_t0', 'heat_t100'):
            if row['unit'] != 'degC':
                raise ValueError(f'Threshold unit must be degC: {key}')
            if not Decimal(row['value']).is_finite():
                raise ValueError(f'Threshold must be finite: {key}')
        if row['value'] and row['param'] in ('frost_window', 'heat_window'):
            if row['value'] != 'all' and not set(row['value'].split('+')) <= {'ini', 'dev', 'mid', 'late'}:
                raise ValueError(f'Invalid sensitive window: {key}')
        indexed[key] = dict(row)
    for crop in CROPS:
        for hazard in ('frost', 'heat'):
            a = indexed.get((crop, hazard + '_t0'), {}).get('value')
            b = indexed.get((crop, hazard + '_t100'), {}).get('value')
            if a and b:
                ordered = Decimal(b) < Decimal(a) if hazard == 'frost' else Decimal(b) > Decimal(a)
                if not ordered:
                    raise ValueError(f'Invalid threshold direction: {crop}/{hazard}')
    required = set(REQUIRED) | {'frost_window', 'heat_window'} | {r['param'] for r in params}
    missing = []
    for crop in CROPS:
        for param in sorted(required):
            if (crop, param) not in indexed:
                # Do not invent per-crop values or turn missing costs into zero.
                row = dict(crop_id=crop, param=param, value='', unit='degC' if param in ('frost_t0', 'frost_t100', 'heat_t0', 'heat_t100') else '', source_id='',
                           conf='P', status='placeholder', nota='No verified value in source snapshot')
                indexed[crop, param] = row
            if indexed[crop, param]['value'] == '' and (param in REQUIRED or param == 'coste_total'):
                missing.append({'crop_id': crop, 'param': param})
    long_rows = [indexed[crop, param] for crop in CROPS for param in sorted(required)]
    # Product rows contain only sourced overrides; agronomy is inherited by the engine.
    long_rows += [indexed[key] for key in sorted(indexed) if key[0] not in CROPS]
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
    cost_rows = [indexed[crop, param] for crop in CROPS for param in cost_params]
    cost_rows += [row for row in costs if row['crop_id'] not in CROPS]
    costs = [dict(cell, source_year='',
                  price_base_year='2018' if cell['value'] and 'EUR' in cell['unit'] else '',
                  monetary_basis='historical_nominal_unadjusted',
                  basis_note='IMIDA base 2018 per Enrique #54 (survey 2017-19); no inflation adjustment')
             for cell in cost_rows]
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
    hicp_path = source / 'eurostat_hicp_es.csv'
    if hicp_path.exists():
        hicp = read(hicp_path)
        years = [r['year'] for r in hicp]
        if len(years) != len(set(years)) or 'EUR-HICP' not in sources:
            raise ValueError('Invalid HICP provenance or duplicate year')
        if any(not Decimal(r['hicp_2015_100']).is_finite() or Decimal(r['hicp_2015_100']) <= 0 for r in hicp):
            raise ValueError('HICP must be finite and positive')
        write(dest / 'eurostat_hicp_es.csv', hicp, list(hicp[0]))
    write(dest / 'sources.csv', source_rows, list(source_rows[0]))
    if products:
        write(dest / 'products.csv', products, list(products[0]))
    candidates = []
    if supplement and (supplement / 'cost_candidates.csv').exists():
        candidates = read(supplement / 'cost_candidates.csv')
        keys = set()
        for row in candidates:
            key = row['crop_id'], row['water_regime'], row['param'], row['source_id']
            if key in keys or row['source_id'] not in sources or row['conf'] != 'B' or row['status'] != 'proxy_candidate':
                raise ValueError(f'Invalid cost candidate: {key}')
            if row['water_regime'] not in ('secano', 'regadio') or row['use'] != 'harvested_grain':
                raise ValueError(f'Invalid cost candidate use: {key}')
            value = Decimal(row['value'])
            if not value.is_finite() or value < 0:
                raise ValueError(f'Invalid candidate cost: {key}')
            keys.add(key)
        write(dest / 'cost_candidates.csv', candidates, list(candidates[0]))
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(source.glob('*.csv'))}
    if supplement:
        hashes.update({'supplement/' + p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted(supplement.glob('*.csv'))})
    manifest = {'source_revision': revision, 'input_sha256': hashes,
                'crops': list(CROPS), 'source_parameter_rows': len(params),
                'products': len(products),
                'excluded_inputs': {'carm_precios_mensuales.csv': 'Not imported: CARM legal notice restricts use to personal non-commercial and disallows modification; human clearance or applicable permission needed.'} if products else {},
                'prices': len(prices), 'missing_required_values': missing,
                'cost_candidates': len(candidates),
                'cost_candidate_policy': 'Not loaded into canonical crop_params/costs: select matching water regime and convert from each native price_base_year before engine evaluation.',
                'optional_window_values': 'Empty means undocumented; engine may apply its explicit all-cycle assumption. Values allowed: all or ini/dev/mid/late joined by +.',
                'price_missing_crops': [c for c in CROPS if c not in {r['crop_id'] for r in prices}],
                'limitations': ['National annual prices are not local farm forecasts.',
                                'No inflation alignment: real2015 prices must not be mixed with historical nominal costs.',
                                'Cover vetch is not harvested forage: forage costs require an explicit proxy decision.',
                                'No missing value has been replaced by zero.'],
                'license_review': {k: 'pending_review' for k in sources
                                   if k.startswith(('F56', 'F29', 'IMIDA', 'RES', 'UC-', 'ECO-', 'KEW-', 'SIAM', 'CARM-'))}}
    (dest / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--revision', required=True)
    ap.add_argument('--supplement', type=Path)
    args = ap.parse_args()
    result = build(args.input, args.output, args.revision, args.supplement)
    print(json.dumps({k: result[k] for k in ('source_revision', 'source_parameter_rows', 'prices')}))
