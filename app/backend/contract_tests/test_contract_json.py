"""Independent output checks requested in bus #180/#181.

Run only this file: python -m pytest app/backend/contract_tests/test_contract_json.py -q
Reads the two committed outputs. Does not rebuild, mutate or repair them, and never
calls validate_v1_1.py. The only product function called is the requested texts.check.
"""
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = ('torre-pacheco.json', 'torre-pacheco.abierto.json')
# Read from v1.1 schema at main f51cc0e, $defs.status, per bus #193.
STATUS_PATTERN = re.compile(r'^(cargando|real|precalculado|simulado)([ :(].*)?$')
LEGAL_RESULTS = {'ok', 'falla', 'no_evaluable'}
INVALID_TEXT = re.compile(r'\b(?:none|nan|null)\b', re.IGNORECASE)
CHECKS = ('source_references', 'open_prices', 'scenario_alignment', 'effective_sample_size',
          'legal_results', 'text_integrity', 'block_statuses')


def walk(node, path='$'):
    """Yield exact field paths, using stable rotation ids instead of opaque list offsets."""
    yield path, node
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f'{path}.{key}')
    elif isinstance(node, list):
        for i, value in enumerate(node):
            label = f'id={value["id"]}' if isinstance(value, dict) and 'id' in value else str(i)
            yield from walk(value, f'{path}[{label}]')


def short(value):
    text = repr(value)
    return text if len(text) <= 180 else text[:177] + '...'


def source_references(doc):
    issues = []
    sources = doc.get('fuentes', [])
    if not isinstance(sources, list):
        return ['$.fuentes: expected a list']
    ids = {r.get('id') for r in sources if isinstance(r, dict) and isinstance(r.get('id'), str)}
    for path, node in walk(doc):
        if isinstance(node, dict) and 'fuente_id' in node:
            value = node['fuente_id']
            if not isinstance(value, str) or value not in ids:
                issues.append(f'{path}.fuente_id: unregistered reference {short(value)}')
    return issues


def open_prices(doc, filename):
    if filename != 'torre-pacheco.abierto.json':
        return []
    issues = []
    for path, node in walk(doc):
        if isinstance(node, dict):
            for key in node:
                if 'carm-anuario' in key.lower() or 'anuarios' in key.lower():
                    issues.append(f'{path}.{key}: prohibited open-output key')
        elif isinstance(node, str) and ('carm-anuario' in node.lower() or 'anuarios' in node.lower()):
            issues.append(f'{path}: CARM-ANUARIO or anuarios remains in open output')
    return issues


def scenario_alignment(doc):
    issues, reference = [], None
    rotations = doc.get('rotaciones', [])
    evaluable = [r for r in rotations if isinstance(r.get('escenarios'), list) and r['escenarios']]
    if not evaluable:
        return ['$.rotaciones: no evaluable scenario sets to compare']
    for r in evaluable:
        path = f'$.rotaciones[id={r.get("id")}]'
        meta = r.get('escenarios_meta')
        if not isinstance(meta, dict):
            issues.append(f'{path}.escenarios_meta: missing scenario metadata')
            continue
        if meta.get('alineados') is not True:
            issues.append(f'{path}.escenarios_meta.alineados: expected true, got {short(meta.get("alineados"))}')
        count = len(r['escenarios'])
        for key in ('anio_clima', 'factor_coste'):
            values = meta.get(key)
            if not isinstance(values, list) or len(values) != count:
                issues.append(f'{path}.escenarios_meta.{key}: expected {count} scenario entries')
            if reference is not None and values != reference[1].get(key):
                other = reference[1].get(key)
                if isinstance(values, list) and isinstance(other, list):
                    first = next((i for i, (a, b) in enumerate(zip(values, other)) if a != b), min(len(values), len(other)))
                    issues.append(f'{path}.escenarios_meta.{key}[{first}]: differs from rotation {reference[0]} at the same scenario index')
                else:
                    issues.append(f'{path}.escenarios_meta.{key}: differs from rotation {reference[0]}')
        if reference is None:
            reference = r.get('id'), meta
    return issues


def effective_sample_size(doc):
    issues = []
    for path, node in walk(doc):
        if not isinstance(node, dict) or not isinstance(node.get('exito_pct'), dict):
            continue
        p = path + '.exito_pct'
        stats = node['exito_pct']
        if stats.get('valor') is None:
            continue  # No success interval or effective sample for a non-evaluable result.
        for name in ('n_efectivo', 'n_anios_historicos'):
            value = stats.get(name)
            if type(value) is not int or value < 1:
                issues.append(f'{p}.{name}: expected a positive integer, got {short(value)}')
        if stats.get('n_efectivo') != stats.get('n_anios_historicos'):
            issues.append(f'{p}: n_efectivo={short(stats.get("n_efectivo"))} != n_anios_historicos={short(stats.get("n_anios_historicos"))}')
    return issues


def legal_results(doc):
    issues = []
    for path, node in walk(doc):
        if not isinstance(node, dict) or 'semaforo_legal' not in node:
            continue
        if path.endswith(('._estado_bloques', '.estado_bloques')):
            continue  # A block-state label is not the legal-check block itself.
        legal = node['semaforo_legal']
        if not isinstance(legal, dict) or not isinstance(legal.get('comprobaciones'), list):
            issues.append(f'{path}.semaforo_legal.comprobaciones: expected a list')
            continue
        for i, check in enumerate(legal['comprobaciones']):
            value = check.get('resultado') if isinstance(check, dict) else None
            if value not in LEGAL_RESULTS:
                issues.append(f'{path}.semaforo_legal.comprobaciones[{i}].resultado: invalid {short(value)}')
    return issues


def text_integrity(doc):
    issues = []
    for path, node in walk(doc):
        if isinstance(node, str) and (match := INVALID_TEXT.search(node)):
            issues.append(f'{path}: literal text token {match.group(0)!r}; JSON null values themselves are allowed')
    # Load this stdlib-only file directly: do not import the engine, generate text or run builds.
    path = ROOT / 'app/backend/engine/decision/texts.py'
    spec = importlib.util.spec_from_file_location('contract_texts_check', path)
    texts = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(texts)
    for rotation, value, sentence in texts.check(doc):
        issues.append(f'$.rotaciones[id={rotation}].texto: texts.check rejected {short(value)} in {short(sentence)}')
    return issues


def block_statuses(doc):
    issues = []
    for path, node in walk(doc):
        if not isinstance(node, dict):
            continue
        # Root _status is a narrative document description, not a block state.
        if path != '$' and '_status' in node and (not isinstance(node['_status'], str) or not STATUS_PATTERN.fullmatch(node['_status'])):
            issues.append(f'{path}._status: invalid block state {short(node["_status"])}; expected v1.1 status prefix')
        for field in ('_estado_bloques', 'estado_bloques'):
            values = node.get(field)
            if isinstance(values, dict):
                for name, value in values.items():
                    # Root legacy map is explicitly string-only, not the status enum.
                    valid = isinstance(value, str) and (field == '_estado_bloques' or STATUS_PATTERN.fullmatch(value))
                    if not valid:
                        issues.append(f'{path}.{field}.{name}: invalid block state {short(value)}')
    return issues


def audit(doc, filename):
    return {name: (open_prices(doc, filename) if name == 'open_prices' else globals()[name](doc)) for name in CHECKS}


@pytest.fixture(scope='module', params=OUTPUTS, ids=OUTPUTS)
def output_audit(request):
    filename = request.param
    doc = json.loads((ROOT / 'app/data' / filename).read_text(encoding='utf-8'))
    return filename, audit(doc, filename)


@pytest.mark.parametrize('criterion', CHECKS)
def test_committed_contract(output_audit, criterion):
    filename, results = output_audit
    assert not results[criterion], filename + ':\n' + '\n'.join(results[criterion])
