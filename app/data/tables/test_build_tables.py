import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('tables', Path(__file__).with_name('build_tables.py'))
tables = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tables)


class TablesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / 'input'
        self.src.mkdir()
        self.out = self.root / 'out'
        tables.write(self.src / 'sources.csv', [dict(source_id='F56-T12'), dict(source_id='EUR-PRICE'),
                                               dict(source_id='EUR-HICP')], ['source_id'])
        fields = ['crop_id', 'param', 'value', *tables.META]
        self.param = dict(crop_id='lechuga', param='kc_ini', value='0.7', unit='-',
                          source_id='F56-T12', conf='A', status='sourced', nota='test fixture')
        tables.write(self.src / 'fao_crop_params.csv', [self.param], fields)
        tables.write(self.src / 'imida_costs.csv', [], fields)
        tables.write(self.src / 'eurostat_prices_es.csv',
                     [dict(crop_id='brocoli', year='2024', eur_100kg='32.07', eur_100kg_real2015='45.03', code='04110000')],
                     ['crop_id', 'year', 'eur_100kg', 'eur_100kg_real2015', 'code'])
        tables.write(self.src / 'eurostat_area_es.csv', [dict(crop_id='brocoli', year='2024')], ['crop_id', 'year'])

    def test_conversion_provenance_gaps_and_reproducibility(self):
        tables.build(self.src, self.out, 'fixture')
        crops = {r['crop_id']: r for r in tables.read(self.out / 'crops.csv')}
        self.assertEqual(len(crops), 8)
        self.assertEqual(crops['lechuga']['kc_ini__source_id'], 'F56-T12')
        self.assertEqual(crops['haba']['zr_min'], '')
        self.assertEqual(crops['haba']['zr_min__conf'], 'P')
        self.assertNotIn('root_depth', crops['haba'])
        price = tables.read(self.out / 'prices.csv')[0]
        self.assertEqual(price['eur_kg'], '0.3207')
        self.assertEqual(price['eur_100kg'], '32.07')
        self.assertEqual(price['status'], 'proxy')
        before = {p.name: p.read_bytes() for p in self.out.iterdir()}
        tables.build(self.src, self.out, 'fixture')
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.out.iterdir()})

    def test_duplicate_parameter_rejected(self):
        tables.write(self.src / 'fao_crop_params.csv', [self.param, self.param], list(self.param))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            tables.build(self.src, self.out, 'fixture')

    def test_unknown_source_rejected(self):
        self.param['source_id'] = 'nonexistent'
        tables.write(self.src / 'fao_crop_params.csv', [self.param], list(self.param))
        with self.assertRaisesRegex(ValueError, 'provenance'):
            tables.build(self.src, self.out, 'fixture')


if __name__ == '__main__':
    unittest.main()
