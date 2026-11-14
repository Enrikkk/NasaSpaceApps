"""H002 policy. Factors change scores only: never euros, yield or probabilities.

The module loads its shipped rule table once; both public functions perform no IO,
make no network requests and never modify their inputs.
"""
import csv
import math
from numbers import Real
from pathlib import Path

TABLE = Path(__file__).with_name('tables') / 'idoneidad.csv'
BASES = ('lechuga', 'brocoli', 'melon', 'alcachofa', 'haba', 'cebada', 'veza', 'limon')
SOIL_FIELDS = ('textura', 'salinidad_ce_dsm', 'ph', 'drenaje', 'profundidad_cm')
# All environmental cutoffs are original, unvalidated project scoring assumptions.
AMBIENTE_UMBRALES = {
    'agua_alto_max_m3_ha': 3000, 'agua_bajo_min_m3_ha': 6000,
    'desnudo_alto_max_dias': 60, 'desnudo_bajo_min_dias': 180,
    'credito_n_alto_min_kg_ha': 30,
}


def _number(value, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, Real):
        return None
    value = float(value)
    if not math.isfinite(value) or (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
        return None
    return value


def _catalog(catalogo):
    items = catalogo.items() if isinstance(catalogo, dict) else ((None, x) for x in catalogo)
    out = []
    for key, item in items:
        if isinstance(item, str):
            ident, base = key or item, item
        elif isinstance(item, dict):
            ident = key or item.get('product_id') or item.get('crop_id') or item.get('id')
            base = item.get('crop_id') or ident
        else:
            ident = key or getattr(item, 'crop_id', None)
            base = getattr(item, 'crop_id', ident)
        if not isinstance(ident, str) or not isinstance(base, str):
            raise ValueError('catalogo requires string IDs and crop_id')
        base = next((c for c in BASES if base == c or base.startswith(c + '_')), base)
        if any(existing == ident for existing, _ in out):
            raise ValueError('duplicate catalog ID: ' + ident)
        out.append((ident, base))
    return out


def _rules():
    with TABLE.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


RULES = tuple(_rules())


def evaluar(parcela_input, catalogo):
    """Return exclusions, score factors and explicit missing-data/rule notices.

    catalogo: list of base/product IDs, list of mappings, or ID->crop_id/mapping.
    A removed entry is listed in excluidos and has factor0 with estado=excluido.
    Unknown soils do not receive invented penalties. Pending rules stay neutral
    even if an input exists; sin_dato explains the missing rule separately.
    """
    soil = parcela_input.get('suelo') or {}
    if not isinstance(soil, dict):
        soil = {}
    values = {'regadio': parcela_input.get('regadio'),
              'pendiente_pct': _number(parcela_input.get('pendiente_pct'), 0)}
    if type(values['regadio']) is not bool:
        values['regadio'] = None
    for name in SOIL_FIELDS:
        v = soil.get(name)
        if name in ('salinidad_ce_dsm', 'profundidad_cm'):
            v = _number(v, 0)
        elif name == 'ph':
            v = _number(v, 0, 14)
        elif not isinstance(v, str) or not v.strip():
            v = None
        values[name] = v
    missing = []
    def gap(crop, field, reason):
        item = {'cultivo': crop, 'campo': field, 'motivo': reason}
        if item not in missing:
            missing.append(item)
    rules = RULES
    result = {'excluidos': [], 'factores': {}, 'sin_dato': missing}
    for ident, base in _catalog(catalogo):
        applicable = [r for r in rules if r['crop_id'] == base]
        entry = {'factor': 1.0, 'motivos': [], 'estado': 'sin_dato', 'factores_aplicados': []}
        result['factores'][ident] = entry
        if not applicable:
            gap(ident, 'cultivo', 'cultivo sin reglas verificadas: no aplicado')
            continue
        for field in ('regadio', 'pendiente_pct') + SOIL_FIELDS:
            if values[field] is None:
                gap(ident, field, 'sin dato valido de ' + field + ': no aplicado')
        for rule in applicable:
            field, op = rule['variable'], rule['operador']
            if op == 'pending':
                gap(ident, field, rule['nota'])
                continue
            value = values[field]
            if value is None:
                continue
            if field == 'salinidad_ce_dsm' and soil.get('salinidad_metodo') != 'ECe':
                gap(ident, field, 'metodo ECe no confirmado: no aplicado')
                continue
            match = ((op == 'eq' and value is False and rule['valores'] == 'false')
                     or (op == 'gt' and value > float(rule['min']))
                     or (op == 'range' and float(rule['min']) < value <= float(rule['max']))
                     or (op == 'outside' and (value < float(rule['min']) or value > float(rule['max'])))
                     or (op == 'in' and isinstance(value, str) and value in rule['valores'].split('|')))
            if not match:
                continue
            applied = {k: rule[k] for k in ('variable', 'factor', 'source_id', 'url', 'licencia', 'conf', 'estado', 'nota', 'umbral_estado')}
            applied['valor_entrada'] = value
            entry['factores_aplicados'].append(applied)
            entry['motivos'].append(rule['nota'])
            if rule['factor'] == 'excluir':
                entry.update(factor=0.0, estado='excluido')
                result['excluidos'].append({'cultivo': ident, 'motivo': rule['nota'], 'source_id': rule['source_id'], 'estado': rule['estado']})
                break
            entry['factor'] *= float(rule['factor'])
            entry['estado'] = rule['estado']
    return result


def etiqueta_ambiental(metricas):
    """Original project label, not LCA, legal compliance or agronomic validation.

    alto=more environmentally friendly under these assumptions. Missing metrics
    never earn an alto: output medio with explicit sin_dato unless a known adverse
    threshold already justifies bajo. Three metrics required for alto. Legal
    falla/no_evaluable prevents alto; absent legal status remains explicit unknown.
    """
    limits = AMBIENTE_UMBRALES
    water = _number(metricas.get('agua_m3_ha'), 0)
    bare = _number(metricas.get('suelo_desnudo_dias'), 0, 366)
    nitrogen = _number(metricas.get('credito_n_kg_ha'), 0)
    legal = metricas.get('semaforo_legal')
    if isinstance(legal, dict):
        legal = legal.get('resultado') or legal.get('color')
    legal = {'verde': 'ok', 'rojo': 'falla', 'gris': 'no_evaluable', 'ambar': 'no_evaluable'}.get(legal, legal)
    missing = [k for k, v in [('agua_m3_ha', water), ('suelo_desnudo_dias', bare), ('credito_n_kg_ha', nitrogen)] if v is None]
    if legal not in ('ok', 'falla', 'no_evaluable'):
        missing.append('semaforo_legal')
    adverse = []
    if water is not None and water >= limits['agua_bajo_min_m3_ha']:
        adverse.append('agua >=6000 m3/ha: umbral supuesto')
    if bare is not None and bare >= limits['desnudo_bajo_min_dias']:
        adverse.append('suelo desnudo >=180 dias: umbral supuesto')
    if legal == 'falla':
        adverse.append('semaforo legal falla: no se oculta con otros indicadores')
    high = (not missing and legal == 'ok' and water <= limits['agua_alto_max_m3_ha']
            and bare <= limits['desnudo_alto_max_dias'] and nitrogen >= limits['credito_n_alto_min_kg_ha'])
    level = 'bajo' if adverse else ('alto' if high else 'medio')
    reasons = adverse or (['agua <=3000, desnudo <=60, credito N >=30 y legal ok: umbrales supuestos'] if high else ['sin evidencia suficiente para alto/bajo segun esta politica supuesta'])
    reasons += ['sin dato valido de ' + name + ': etiqueta incompleta' for name in missing]
    return {'nivel': level, 'motivos': reasons, 'estado': 'supuesto', 'sin_dato': missing,
            'umbrales': dict(limits), 'nota': 'Etiqueta heuristica; alto significa mas amigable bajo estos supuestos, no certificacion ambiental/legal.'}
