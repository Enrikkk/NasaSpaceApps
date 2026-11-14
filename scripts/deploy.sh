#!/usr/bin/env bash
# T-017: read-only local preparation. This command never deploys or modifies cloud resources.
set -euo pipefail
TASK_REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
python3 - "$TASK_REPO" "$@" <<'PY'
import argparse
import ast
import hashlib
import importlib.metadata
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description='T-017 local preparation only; no network, cloud calls, installs or writes.')
parser.add_argument('mode', choices=('inspect', 'check-image', 'check-demo'), nargs='?', default='inspect')
parser.add_argument('--root', type=Path, default=Path(sys.argv[1]))
parser.add_argument('--engine-json', type=Path, help='Optional existing demo-engine JSON to inspect; not copied into the image.')
args = parser.parse_args(sys.argv[2:])
root = args.root.resolve()
pending, warnings, errors = [], [], []
files = {}

def require(relative):
    p = root / relative
    if not p.exists():
        pending.append('Missing input: ' + relative)
        return False
    members = [p] if p.is_file() else sorted(p.rglob('*'))
    for member in members:
        if not member.is_file() or '__pycache__' in member.parts or member.suffix == '.pyc':
            continue
        name = str(member.relative_to(root))
        files[name] = hashlib.sha256(member.read_bytes()).hexdigest()
        if member.suffix == '.py':
            try:
                ast.parse(member.read_text(encoding='utf-8'))
            except SyntaxError:
                errors.append('Invalid Python syntax: ' + name)
    return True

def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        errors.append(f'Invalid JSON {path.name}: {type(e).__name__}')
        return None

def git(*commands):
    r = subprocess.run(['git', '-C', str(root), *commands], text=True, capture_output=True)
    return r.stdout.strip() if r.returncode == 0 else None

api = root / 'app/backend/api'
dockerfile = api / 'Dockerfile'
copy_inputs = []
if require('app/backend/api/Dockerfile'):
    logical = dockerfile.read_text().replace('\\\n', ' ')
    for line in logical.splitlines():
        if not line.lstrip().startswith('COPY '):
            continue
        parts = shlex.split(line.strip())[1:]
        if any(p.startswith('--') for p in parts) or line.strip().startswith('COPY ['):
            errors.append('Unsupported COPY form; review Dockerfile before using this checker')
            continue
        for src in parts[:-1]:
            copy_inputs.append(src)
            require(src)
    if 'USER app' not in logical or '${PORT:-8080}' not in logical:
        errors.append('Docker non-root user / PORT contract changed; review required')

for p in ('app/backend/api/Dockerfile.dockerignore', 'app/backend/api/requirements.txt',
          'app/backend/api/smoke.py', 'app/data/contract.schema.json',
          'app/data/contract/validate_contract.py'):
    require(p)

atom = api / 'atom_build'
gz = sorted(atom.glob('*_recintos.geojson.gz'))
if not gz:
    pending.append('Image needs a producer-supplied ATOM package in app/backend/api/atom_build (not just the viewport sample)')
for path in gz:
    require(str(path.relative_to(root)))
index = atom / 'index.json'
atom_meta = read_json(index) if index.exists() else None
if gz and not index.exists():
    warnings.append('ATOM index.json missing: lookup permits this, municipality/provenance metadata may be absent')
if atom.exists() and git('check-ignore', str(atom.relative_to(root))) is not None:
    warnings.append('ATOM package is git-ignored: verify gcloud upload manifest separately before any future remote build')

seed = root / 'app/data/cache/pipeline/clima_suelo'
seed_files = sorted(seed.glob('*.json'))
if not seed_files:
    pending.append('Missing climate/soil demo seed cache')
for path in seed_files:
    require(str(path.relative_to(root)))
    read_json(path)
sample = root / 'app/data/torre-pacheco.contract.example.json'
sample_doc = read_json(sample) if sample.exists() else None
if sample_doc:
    warnings.append('Default CONTRACT_PATH is the sample contract: rotations/history/NDVI are not a point-specific engine')
    require(str(sample.relative_to(root)))

engine = None
if args.engine_json:
    path = args.engine_json.resolve()
    doc = read_json(path)
    if doc:
        engine = {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                  'licencia': doc.get('licencia'), 'scenario_alignment': doc.get('escenarios_meta', {}).get('alineados')}
        if doc.get('licencia', {}).get('incluye_precios_carm'):
            warnings.append('Selected engine JSON declares CARM prices; publication is not authorized by this preparation')
        staged_engine = root / 'app/backend/api/engine_data/engine.json'
        if 'app/backend/api/engine_data' in copy_inputs:
            if not staged_engine.exists():
                warnings.append('Dockerfile copies engine_data, but engine.json is absent: use the producer staging/mount contract; never silently rely on DraftEngine')
            elif sha256 := hashlib.sha256(staged_engine.read_bytes()).hexdigest():
                if sha256 != engine['sha256']:
                    warnings.append('Staged engine_data/engine.json differs from the explicitly inspected JSON')
        else:
            warnings.append('ENGINE_JSON only inspected: this Dockerfile does not copy engine_data; use a producer-defined mount/integration')

frontend = root / 'app/frontend'
package = frontend / 'package.json'
frontend_scripts = None
if package.exists():
    doc = read_json(package)
    frontend_scripts = doc.get('scripts', {}) if doc else None
else:
    pending.append('Frontend has no versioned package.json: build/preview and preloaded browser fallback cannot be checked')
if not (frontend / 'dist/index.html').is_file():
    pending.append('No frontend dist/index.html supplied by Jaime')
pending.append('No verified browser demo fallback or production frontend origin supplied')

tools = {name: bool(shutil.which(name)) for name in ('python3', 'docker', 'node', 'npm')}
if not tools['docker']:
    pending.append('Docker unavailable locally: image build/run and network-disabled smoke are unverified')
versions = {}
for name in ('fastapi', 'uvicorn', 'numpy', 'shapely', 'jsonschema', 'pytest'):
    try:
        versions[name] = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        versions[name] = None

image_pending = [p for p in pending if 'Frontend' not in p and 'frontend' not in p and 'browser' not in p]
report = {'scope': 'Local inspection only; no deploy, cloud changes, installs or source edits',
          'mode': args.mode, 'commit': git('rev-parse', 'HEAD'), 'dirty': bool(git('status', '--porcelain')),
          'root': str(root), 'docker_context': 'repository root', 'docker_copy_inputs': copy_inputs,
          'input_sha256': files, 'atom_files': len(gz), 'atom_metadata_present': atom_meta is not None,
          'pipeline_seed_files': len(seed_files), 'engine_json': engine,
          'frontend_scripts': frontend_scripts, 'tools_available': tools, 'python_packages': versions,
          'schema_validation': 'not run (JSON syntax only); use producer validator in its pinned development environment',
          'warnings': warnings, 'pending': pending, 'errors': errors,
          'source_inspection_completed': not errors,
          'image_build_prerequisites_met': not errors and not image_pending,
          'demo_ready': False}
print(json.dumps(report, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)
if args.mode == 'check-image' and image_pending:
    raise SystemExit(2)
if args.mode == 'check-demo' and pending:
    raise SystemExit(2)
PY
