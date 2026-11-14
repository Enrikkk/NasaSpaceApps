import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('gate', Path(__file__).with_name('t017_frontend_gate.py'))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class FrontendGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dist = Path(self.temp.name)
        (self.dist / 'assets').mkdir()
        (self.dist / 'index.html').write_text('<script type="module" src="./assets/app.js"></script>')
        (self.dist / 'assets/app.js').write_text('console.log("fixture")')

    def worker(self):
        (self.dist / 'assets/worker.mjs').write_text('self.onmessage = () => {};')

    def test_missing_worker_is_failure(self):
        result = gate.inspect(self.dist, 'assets/worker.mjs')
        self.assertFalse(result['passed'])
        self.assertFalse(next(c for c in result['checks'] if c['name'] == 'worker_asset')['ok'])

    def test_html_200_fallback_is_not_a_working_worker(self):
        self.worker()
        def request(url):
            return 200, {'Content-Type': 'text/html'}, b'<!doctype html><html>app fallback</html>'
        result = gate.inspect(self.dist, 'assets/worker.mjs', 'http://localhost:4173', request=request)
        self.assertFalse(result['passed'])

    def test_origin_difference_rejected(self):
        def request(url, **kwargs):
            if url.endswith('/health'):
                return 200, {}, b'{"status":"ok","version":"fixture"}'
            return 200, {'Access-Control-Allow-Origin': 'http://localhost:5173',
                         'Access-Control-Allow-Methods': 'GET,POST',
                         'Access-Control-Allow-Headers': 'Content-Type'}, b''
        result = gate.inspect(self.dist, api_base='https://example.invalid',
                              origin='http://127.0.0.1:5173', request=request)
        self.assertFalse(result['passed'])

    def test_passing_checks_never_certify_demo(self):
        self.worker()
        def request(url, **kwargs):
            if url.endswith('/health'):
                return 200, {}, b'{"status":"ok"}'
            if url.endswith('/analyze'):
                return 204, {'Access-Control-Allow-Origin': 'http://127.0.0.1:5173',
                             'Access-Control-Allow-Methods': 'POST',
                             'Access-Control-Allow-Headers': 'content-type'}, b''
            return 200, {'Content-Type': 'text/javascript; charset=utf-8'}, b'self.onmessage=()=>{}'
        result = gate.inspect(self.dist, 'assets/worker.mjs', 'http://localhost:4173/demo',
                              'https://example.invalid', 'http://127.0.0.1:5173', request)
        self.assertTrue(result['passed'])
        self.assertFalse(result['demo_ready'])
        self.assertFalse(result['browser_flow_verified'])
        self.assertEqual(len(result['files_sha256']), 3)

    def test_paths_cannot_escape_dist(self):
        (self.dist / 'index.html').write_text('<script src="../private.js"></script>')
        result = gate.inspect(self.dist)
        self.assertFalse(result['passed'])

    def test_credentials_cors_is_not_accepted(self):
        self.assertFalse(gate.cors_allowed(200, {
            'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Credentials': 'true'},
            'http://localhost:5173'))


if __name__ == '__main__':
    unittest.main()
