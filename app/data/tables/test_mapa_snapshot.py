import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location('mapa', Path(__file__).with_name('build_mapa_snapshot.py'))
mapa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mapa)


class ExtractionTests(unittest.TestCase):
    def fixture(self, path, annual='54.47', unit='100 KG.'):
        # Minimal source workbook with a deliberately different monthly value.
        with ZipFile(path, 'w') as z:
            z.writestr('xl/sharedStrings.xml', '<sst xmlns="' + mapa.NS['s'] + '">' +
                       ''.join('<si><t>' + s + '</t></si>' for s in
                               ('PRODUCTOS', 'AÑO', 'Anual', 'LECHUGA (' + unit + ')')) + '</sst>')
            z.writestr('xl/workbook.xml', '<workbook xmlns="' + mapa.NS['s'] +
                       '" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                       '<sheets><sheet name="PrePer3" r:id="rId4"/></sheets></workbook>')
            z.writestr('xl/_rels/workbook.xml.rels', '<Relationships><Relationship Id="rId4" '
                       'Target="worksheets/not-sheet3.xml"/></Relationships>')
            z.writestr('xl/styles.xml', '<styleSheet xmlns="' + mapa.NS['s'] +
                       '"><cellXfs><xf numFmtId="2"/></cellXfs></styleSheet>')
            z.writestr('docProps/core.xml', '<coreProperties><modified>2026-01-01</modified></coreProperties>')
            z.writestr('xl/worksheets/not-sheet3.xml', '<worksheet xmlns="' + mapa.NS['s'] + '"><sheetData>'
                       '<row><c r="A4" t="s"><v>0</v></c><c r="B4" t="s"><v>1</v></c>'
                       '<c r="O4" t="s"><v>2</v></c></row>'
                       '<row><c r="A5" t="s"><v>3</v></c><c r="B5"><v>2005</v></c>'
                       '<c r="C5"><v>999</v></c><c r="O5"><v>' + annual + '</v></c></row>'
                       '<row><c r="B6"><v>2006</v></c><c r="O6"><v>61.56</v></c></row>'
                       '</sheetData></worksheet>')

    def test_named_sheet_annual_column_and_merged_label(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.xlsx'
            self.fixture(path)
            rows, _, _ = mapa.extract(path)
            self.assertEqual(rows['lechuga', 2005]['eur_100kg'], '54.47')
            self.assertEqual(rows['lechuga', 2006]['source_cell'], 'O6')

    def test_invalid_prices_and_piece_units_rejected(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.xlsx'
            for value in ('NaN', 'Infinity', '0', '-1'):
                self.fixture(path, annual=value)
                with self.assertRaises(ValueError):
                    mapa.extract(path)
            self.fixture(path, unit='100 UD.')
            with self.assertRaisesRegex(ValueError, 'unit'):
                mapa.extract(path)


if __name__ == '__main__':
    unittest.main()
