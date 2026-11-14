"""Tests de la localizacion del esquema del contrato (sin red ni dependencias externas)."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app.backend.pipeline import contract


class TestContract(unittest.TestCase):
    def test_orden_y_ultimo_recurso(self):
        self.assertEqual([p.name for p in contract.CANDIDATOS],
                         ["contract.schema.json", "contract.schema.v1.1.json", "contract.schema.json"])
        self.assertEqual(contract.CANDIDATOS[0], contract.REPO_ROOT / "app" / "data" / "contract.schema.json")

    def test_sin_esquema_no_lanza(self):
        with mock.patch.object(contract, "CANDIDATOS", ()), mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("AGROCKHAM_CONTRACT_SCHEMA", None)
            self.assertIsNone(contract.schema_path())
            self.assertEqual(contract.load_schema(), (None, None))

    def test_prefiere_el_primero_que_existe(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "a.json", Path(d) / "b.json"
            b.write_text(json.dumps({"x": 2}))
            with mock.patch.object(contract, "CANDIDATOS", (a, b)):
                os.environ.pop("AGROCKHAM_CONTRACT_SCHEMA", None)
                self.assertEqual(contract.schema_path(), b)  # a no existe: cae al siguiente
                a.write_text(json.dumps({"x": 1}))
                self.assertEqual(contract.load_schema()[0], {"x": 1})

    def test_variable_de_entorno_manda(self):
        with tempfile.TemporaryDirectory() as d:
            e = Path(d) / "env.json"
            e.write_text("{}")
            with mock.patch.dict(os.environ, {"AGROCKHAM_CONTRACT_SCHEMA": str(e)}):
                self.assertEqual(contract.schema_path(), e)

    def test_hay_esquema_en_el_repo(self):
        self.assertIsNotNone(contract.schema_path())


if __name__ == "__main__":
    unittest.main()
