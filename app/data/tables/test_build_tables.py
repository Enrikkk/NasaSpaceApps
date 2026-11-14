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

    def test_composite_source_and_threshold_contract(self):
        self.param.update(param='stages_days_murcia', value='34/34/211/25', source_id='F56-T12+EUR-PRICE')
        tables.write(self.src / 'fao_crop_params.csv', [self.param], list(self.param))
        tables.build(self.src, self.out, 'fixture')
        crops = {r['crop_id']: r for r in tables.read(self.out / 'crops.csv')}
        self.assertEqual(crops['lechuga']['frost_t100'], '')
        self.assertEqual(crops['lechuga']['frost_t100__unit'], 'degC')
        self.assertNotIn('frost_threshold', crops['lechuga'])
        self.param.update(param='heat_window', value='flowering')
        tables.write(self.src / 'fao_crop_params.csv', [self.param], list(self.param))
        with self.assertRaisesRegex(ValueError, 'sensitive window'):
            tables.build(self.src, self.out, 'fixture')

    def test_hicp_export_and_invalid_index(self):
        path = self.src / 'eurostat_hicp_es.csv'
        tables.write(path, [dict(year='2025', hicp_2015_100='126.65')], ['year', 'hicp_2015_100'])
        tables.build(self.src, self.out, 'fixture')
        self.assertEqual(tables.read(self.out / path.name)[0]['hicp_2015_100'], '126.65')
        for value in ('0', 'NaN', 'Infinity'):
            tables.write(path, [dict(year='2025', hicp_2015_100=value)], ['year', 'hicp_2015_100'])
            with self.assertRaisesRegex(ValueError, 'finite and positive'):
                tables.build(self.src, self.out, 'fixture')

    def test_nonfinite_and_inverted_thresholds(self):
        for hazard in ('frost', 'heat'):
            for value in ('NaN', 'Infinity', '-Infinity'):
                row = dict(self.param, param=hazard + '_t0', value=value, unit='degC')
                tables.write(self.src / 'fao_crop_params.csv', [row], list(row))
                with self.assertRaisesRegex(ValueError, 'finite'):
                    tables.build(self.src, self.out, 'fixture')
            for b in ('0', '2' if hazard == 'frost' else '-2'):
                rows = [dict(self.param, param=hazard + '_t0', value='0', unit='degC'),
                        dict(self.param, param=hazard + '_t100', value=b, unit='degC')]
                tables.write(self.src / 'fao_crop_params.csv', rows, list(rows[0]))
                with self.assertRaisesRegex(ValueError, 'direction'):
                    tables.build(self.src, self.out, 'fixture')


if __name__ == '__main__':
    unittest.main()
