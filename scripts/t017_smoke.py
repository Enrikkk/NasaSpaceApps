#!/usr/bin/env python3
"""Run a bounded LOCAL API + engine-JSON smoke. No cloud calls, deploys or downloads.

Run with the API producer's pinned development Python. Responses and logs stay outside git.
Docker mode requires an existing local image and uses --pull=never --network none.
"""
import argparse
import gzip
import hashlib
import importlib.metadata
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

DEMO = {'lat': 37.7383, 'lon': -0.98838}
HTTP_CLIENT = '''import json,sys,urllib.request,urllib.error
q=json.loads(sys.argv[1]); raw=json.dumps(q['body']).encode() if q['body'] is not None else None
r=urllib.request.Request(q['url'],data=raw,method=q['method'],headers=q['headers'])
try:
 h=urllib.request.urlopen(r,timeout=20)
except urllib.error.HTTPError as e:
 h=e
print(json.dumps({'status':h.code,'headers':dict(h.headers),'body':json.load(h)}))
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True, help='Existing candidate checkout; never modified')
    ap.add_argument('--engine-json', type=Path, required=True)
    ap.add_argument('--atom-dir', type=Path)
    ap.add_argument('--sample-atom', action='store_true', help='Explicitly use the committed 66-feature sample, not full municipal coverage')
    ap.add_argument('--mode', choices=('local', 'docker'), default='local')
    ap.add_argument('--image', help='Existing local image for Docker mode; never built or pulled here')
    ap.add_argument('--api-sha', default='unrecorded')
    ap.add_argument('--engine-sha', default='unrecorded')
    ap.add_argument('--output', type=Path, help='New report directory outside any working checkout')
    args = ap.parse_args()
    root, engine = args.root.resolve(), args.engine_json.resolve()
    if bool(args.atom_dir) == bool(args.sample_atom):
        ap.error('Choose exactly one of --atom-dir or --sample-atom')
    if not engine.is_file():
        ap.error('Missing engine JSON; no fallback to the draft is allowed in this smoke')
    if args.mode == 'docker' and (not args.image or not shutil.which('docker')):
        ap.error('Docker mode needs Docker and an explicit existing --image; nothing will be installed')
    out = (args.output or Path(tempfile.mkdtemp(prefix='agrockham-t017-smoke-'))).resolve()
    for checkout in (root, Path(__file__).resolve().parents[1]):
        if out == checkout or checkout in out.parents:
            ap.error('Reports must stay outside the candidate and task checkout (responses may contain restricted prices)')
    if args.output:
        out.mkdir(parents=True, exist_ok=False)
    report = {'mode': args.mode, 'api_sha': args.api_sha, 'engine_sha': args.engine_sha,
              'engine_sha256': sha(engine), 'checks': [], 'failures': [],
              'offline': 'AGROCKHAM_OFFLINE=1', 'artifacts': str(out),
              'scope': 'API with precomputed demo JSON; not a browser demo, live engine per point or deployment',
              'publication_authorized': False}
    report['python'] = sys.version.split()[0]
    report['runtime_versions'] = {}
    for name in ('fastapi', 'uvicorn', 'numpy', 'shapely', 'jsonschema'):
        try:
            report['runtime_versions'][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            report['runtime_versions'][name] = None
    process, container, log = None, None, None

    def check(name, ok, detail=None):
        item = {'name': name, 'ok': bool(ok)}
        if detail is not None:
            item['detail'] = detail
        report['checks'].append(item)
        if not ok:
            report['failures'].append(name)

    def cmd(argv, **kw):
        return subprocess.run(argv, capture_output=True, text=True, timeout=kw.pop('timeout', 30), **kw)

    def request(method, path, body=None):
        query = {'url': base + path, 'method': method, 'body': body,
                 'headers': {'Content-Type': 'application/json', 'Origin': 'http://localhost:5173'}}
        if container:
            p = cmd(['docker', 'exec', container, 'python3', '-c', HTTP_CLIENT, json.dumps(query)])
            if p.returncode:
                raise RuntimeError('Container HTTP client failed: ' + p.stderr[-500:])
            return json.loads(p.stdout)
        raw = json.dumps(body).encode() if body is not None else None
        q = urllib.request.Request(query['url'], data=raw, method=method, headers=query['headers'])
        try:
            response = urllib.request.urlopen(q, timeout=20)
        except urllib.error.HTTPError as e:
            response = e
        return {'status': response.code, 'headers': dict(response.headers), 'body': json.load(response)}

    def save_validate(name, response):
        path = out / (name + '.json')
        path.write_text(json.dumps(response['body'], ensure_ascii=False, indent=2))
        validator = root / 'app/data/contract/validate_contract.py'
        p = cmd([sys.executable, str(validator), str(path), '--schema', str(root / 'app/data/contract.schema.json')])
        (out / (name + '-validation.txt')).write_text(p.stdout + p.stderr)
        check(name + '-producer-schema-and-invariants', p.returncode == 0,
              'Full validator output retained locally; warnings are not publication approval')

    try:
        engine_doc = json.loads(engine.read_text())
        expected_ids = {r['id'] for r in engine_doc['rotaciones']}
        report['engine_licencia'] = engine_doc.get('licencia')
        report['input_sha256'] = {str(p.relative_to(root)): sha(p) for p in
            (root / 'app/backend/api/main.py', root / 'app/backend/api/engine_adapter.py',
             root / 'app/backend/api/requirements.txt', root / 'app/data/contract.schema.json',
             root / 'app/data/contract/validate_contract.py')}
        if args.sample_atom:
            source = root / 'app/data/cache/pipeline/atom/torre-pacheco_demo_viewport.geojson'
            fc = json.loads(source.read_text())
            atom = out / 'atom-sample'
            atom.mkdir()
            # Re-encode existing FEGA sample features for the producer loader, without fetching or changing attributes.
            with gzip.open(atom / '30037_recintos.geojson.gz', 'wt', encoding='utf-8') as f:
                f.write('{"type":"FeatureCollection","features":[\n')
                f.write(',\n'.join(json.dumps(x, separators=(',', ':')) for x in fc['features']))
                f.write('\n]}\n')
            report['atom'] = {'kind': 'committed viewport sample', 'features': len(fc['features']),
                              'source_sha256': sha(source), 'attribution': fc.get('attribution'),
                              'full_municipal_coverage': False}
        else:
            atom = args.atom_dir.resolve()
            report['atom'] = {'kind': 'producer package', 'files': {p.name: sha(p) for p in sorted(atom.glob('*')) if p.is_file()},
                              'full_municipal_coverage': 'not inferred by smoke'}
        if not list(atom.glob('*_recintos.geojson.gz')):
            raise ValueError('No loader-format ATOM files; refusing a health-only pass')
        if args.mode == 'local':
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            base = f'http://127.0.0.1:{port}'
            env = dict(os.environ, AGROCKHAM_OFFLINE='1', PYTHONDONTWRITEBYTECODE='1',
                       PYTHONPATH=str(root), ENGINE_JSON=str(engine), ATOM_BUILD_DIR=str(atom),
                       PIPELINE_CACHE_DIR=str(out / 'cache'), AGROCKHAM_CACHE_DIR=str(out / 'cache'),
                       GIT_SHA=args.api_sha, FRONTEND_ORIGIN='http://localhost:5173')
            log = (out / 'server.log').open('w')
            process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.backend.api.main:app',
                                        '--host', '127.0.0.1', '--port', str(port)],
                                       cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
            report['network_isolation'] = 'pipeline offline flag; no OS network namespace isolation'
        else:
            container = 'agrockham-t017-' + uuid.uuid4().hex[:12]
            # Container uid 10001 needs read access to this temporary sample mount; source inputs are untouched.
            out.chmod(0o755)
            atom.chmod(0o755) if args.sample_atom else None
            mount_engine = out / 'engine-input.json'
            shutil.copyfile(engine, mount_engine)
            mount_engine.chmod(0o644)
            argv = ['docker', 'run', '--rm', '-d', '--pull=never', '--network', 'none', '--name', container,
                    '--mount', f'type=bind,src={mount_engine},dst=/t017/engine.json,readonly',
                    '--mount', f'type=bind,src={atom},dst=/t017/atom,readonly',
                    '-e', 'AGROCKHAM_OFFLINE=1', '-e', 'ENGINE_JSON=/t017/engine.json',
                    '-e', 'ATOM_BUILD_DIR=/t017/atom', '-e', 'GIT_SHA=' + args.api_sha,
                    '-e', 'FRONTEND_ORIGIN=http://localhost:5173', args.image]
            p = cmd(argv)
            if p.returncode:
                raise RuntimeError('Docker start failed: ' + p.stderr[-1000:])
            info = cmd(['docker', 'inspect', '--format', '{{.HostConfig.NetworkMode}}', container])
            check('container-network-none', info.returncode == 0 and info.stdout.strip() == 'none')
            report['network_isolation'] = 'Docker --network none; client uses docker exec over container loopback'
            base = 'http://127.0.0.1:8080'
        deadline = time.monotonic() + 25
        while True:
            try:
                health = request('GET', '/health')
                break
            except Exception:
                if time.monotonic() >= deadline or (process and process.poll() is not None):
                    raise RuntimeError('API did not become healthy; see server log')
                time.sleep(0.25)
        h = health['body']
        check('health-http-200', health['status'] == 200 and h.get('status') == 'ok')
        check('health-version', h.get('version') == args.api_sha)
        check('atom-loaded-nonempty', h.get('recintos', {}).get('cargado') and h['recintos']['n'] > 0,
              h.get('recintos'))
        analyzed = request('POST', '/analyze', DEMO)
        check('analyze-http-200', analyzed['status'] == 200)
        save_validate('analyze', analyzed)
        d = analyzed['body']
        meta = d.get('_meta', {})
        check('engine-json-selected-no-draft-fallback', 'JSON de enrique' in str(meta.get('motor')), meta.get('motor'))
        check('engine-rotation-ids', {r.get('id') for r in d.get('rotaciones', [])} == expected_ids)
        check('localhost-cors', any(k.lower() == 'access-control-allow-origin' and v == 'http://localhost:5173'
                                    for k, v in analyzed['headers'].items()))
        report['analyze_states'] = meta.get('estado_bloques')
        report['analyze_avisos'] = meta.get('avisos')
        qid = meta.get('consulta_id')
        if not qid:
            check('parcel-query-id', False)
        else:
            parcel = request('GET', '/parcel/' + urllib.parse.quote(str(qid), safe=''))
            check('parcel-http-200', parcel['status'] == 200)
            save_validate('parcel', parcel)
        recintos = request('GET', '/recintos?bbox=-0.990,37.737,-0.987,37.740')
        fc = recintos['body']
        check('recintos-http-200-geojson', recintos['status'] == 200 and fc.get('type') == 'FeatureCollection')
        check('recintos-nonempty', bool(fc.get('features')), len(fc.get('features', [])))
        check('recintos-attribution', bool(fc.get('attribution')))
        report['recintos_count_in_bbox'] = len(fc.get('features', []))
        report['demo_ready'] = False
    except Exception as exc:
        check('runner-completed', False, f'{type(exc).__name__}: {exc}')
    finally:
        if process:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        if container:
            p = cmd(['docker', 'logs', container])
            (out / 'server.log').write_text(p.stdout + p.stderr)
            cmd(['docker', 'stop', '-t', '5', container], timeout=15)
        if log:
            log.close()
        report['passed'] = not report['failures']
        report['demo_ready'] = False
        (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'checks': len(report['checks']), 'failures': report['failures'],
                      'report': str(out / 'report.json'), 'demo_ready': False}, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
