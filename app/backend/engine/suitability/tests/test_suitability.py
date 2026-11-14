import copy
import importlib.util
import math
from pathlib import Path

import pytest

# Direct file import avoids importing engine/scipy; dependency is stdlib + pytest.
P = Path(__file__).resolve().parents[1] / 'suitability.py'
spec = importlib.util.spec_from_file_location('parcel_suitability', P)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


@pytest.mark.parametrize('crop', ['lechuga_iceberg','brocoli','melon_galia','alcachofa'])
def test_dryland_excludes_irrigated_system(crop):
    out=s.evaluar({'regadio':False},[crop])
    assert out['excluidos'][0]['cultivo']==crop
    assert out['factores'][crop]['factor']==0
    assert out['excluidos'][0]['estado']=='supuesto'


@pytest.mark.parametrize('crop',['haba','cebada','veza'])
def test_dryland_retention_does_not_claim_economic_viability(crop):
    out=s.evaluar({'regadio':False,'pendiente_pct':40},[crop])
    assert out['excluidos']==[]
    assert out['factores'][crop]['factor']==1
    assert any(x['campo']=='regadio' for x in out['sin_dato'])


@pytest.mark.parametrize('slope,expected',[(10,1),(10.01,.85),(20,.85),(20.01,.65),(100,.65),(150,.65)])
def test_slope_boundaries_and_crop_list(slope,expected):
    out=s.evaluar({'regadio':True,'pendiente_pct':slope},['lechuga','cebada'])
    assert out['factores']['lechuga']['factor']==expected
    assert out['factores']['cebada']['factor']==1
    if expected<1:assert out['factores']['lechuga']['estado']=='supuesto'


def test_nulls_are_neutral_and_explicit():
    out=s.evaluar({'suelo':None},['brocoli'])
    assert out['factores']['brocoli']['factor']==1
    assert {x['campo'] for x in out['sin_dato']} >= {'regadio','pendiente_pct','ph','drenaje','textura','profundidad_cm','salinidad_ce_dsm'}


@pytest.mark.parametrize('invalid',[float('nan'),float('inf'),-1,float('-inf'),True,'20'])
def test_invalid_slope_is_neutral(invalid):
    out=s.evaluar({'pendiente_pct':invalid},['lechuga'])
    assert out['factores']['lechuga']['factor']==1
    assert any(x['campo']=='pendiente_pct' for x in out['sin_dato'])


def test_no_mutation_no_economics():
    parcel={'regadio':True,'pendiente_pct':25,'margen_eur_ha':500,'suelo':{'ph':7}}
    catalog=[{'product_id':'melon_galia','crop_id':'melon','margen_eur_ha':123}]
    before=copy.deepcopy((parcel,catalog))
    out=s.evaluar(parcel,catalog)
    assert (parcel,catalog)==before
    assert out['factores']['melon_galia']['factor']==.65
    assert 'margen_eur_ha' not in str(out)


def test_mapping_catalog_preserves_product_id():
    out=s.evaluar({'regadio':False},{'x':{'crop_id':'lechuga'}})
    assert out['excluidos'][0]['cultivo']=='x'


def test_unknown_crop_has_no_fabricated_rules():
    out=s.evaluar({'regadio':False},['alcaparra'])
    assert out['factores']['alcaparra']['factor']==1
    assert out['sin_dato'][0]['campo']=='cultivo'


def test_pending_soil_rule_is_not_assumed_suitability():
    out=s.evaluar({'suelo':{'ph':2,'salinidad_ce_dsm':80}},['limon'])
    assert out['factores']['limon']['factor']==1
    assert any('no aplicado' in x['motivo'] for x in out['sin_dato'] if x['campo']=='ph')


@pytest.mark.parametrize('water,bare,n,legal,expected',[
 (3000,60,30,'ok','alto'),(3000.01,60,30,'ok','medio'),
 (3000,60.01,30,'ok','medio'),(3000,60,29.99,'ok','medio'),
 (5999.99,179.99,0,'ok','medio'),(6000,60,30,'ok','bajo'),
 (100,180,30,'ok','bajo'),(100,10,100,'falla','bajo'),
 (100,10,100,'no_evaluable','medio'),(100,10,100,None,'medio'),
 (None,None,None,None,'medio'),(float('inf'),10,100,'ok','medio'),
 (100,10,100,'verde','alto'),(100,10,100,'gris','medio'),
])
def test_environment_boundaries(water,bare,n,legal,expected):
    metrics={'agua_m3_ha':water,'suelo_desnudo_dias':bare,'credito_n_kg_ha':n,'semaforo_legal':legal}
    out=s.etiqueta_ambiental(metrics)
    assert out['nivel']==expected
    assert out['estado']=='supuesto'
    assert out['motivos']


def test_environment_constants_not_mutable_through_result():
    out=s.etiqueta_ambiental({})
    out['umbrales']['agua_alto_max_m3_ha']=9999
    assert s.AMBIENTE_UMBRALES['agua_alto_max_m3_ha']==3000

@pytest.mark.parametrize('ph,expected',[(6.49,.9),(6.5,1),(9,1),(9.01,.9)])
def test_haba_ph_source_separate_from_score_assumption(ph,expected):
    out=s.evaluar({'suelo':{'ph':ph}},['haba'])
    entry=out['factores']['haba']
    assert entry['factor']==expected
    if expected<1:
        assert entry['factores_aplicados'][0]['umbral_estado']=='con_fuente'
        assert entry['factores_aplicados'][0]['estado']=='supuesto'


def test_haba_poor_drainage_combines_score_factors_only():
    out=s.evaluar({'suelo':{'ph':6,'drenaje':'mal_drenado'}},['haba'])
    assert out['factores']['haba']['factor']==pytest.approx(.9*.85)
    assert len(out['factores']['haba']['factores_aplicados'])==2


def test_bundled_rules_are_finite_and_provenance_complete():
    for r in s.RULES:
        assert r['crop_id'] in s.BASES
        assert r['estado'] in ('supuesto','con_fuente')
        assert r['source_id'] and r['url'].startswith('https://') and r['licencia']
        if r['factor']!='excluir':
            factor=float(r['factor'])
            assert math.isfinite(factor) and 0<=factor<=1
        for key in ('min','max'):
            if r[key]:assert math.isfinite(float(r[key]))
        if r['min'] and r['max']:assert float(r['min'])<float(r['max'])


def test_evaluation_does_not_read_again_or_use_network(monkeypatch):
    monkeypatch.setattr(s,'_rules',lambda:pytest.fail('public evaluation must not read a file'))
    assert s.evaluar({'regadio':True},['haba'])['factores']['haba']['factor']==1
