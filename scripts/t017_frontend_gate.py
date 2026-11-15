#!/usr/bin/env python3
"""Read-only frontend readiness checks. Never installs, builds, deploys or certifies the full demo."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request


class Entries(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'script' and a.get('src'):
            self.urls.append(a['src'])
        if tag == 'link' and a.get('href') and a.get('rel') in ('stylesheet', 'modulepreload'):
            self.urls.append(a['href'])


def local_asset(root, url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme or parsed.netloc:
        raise ValueError('External asset: ' + url)
    path = (root / urllib.parse.unquote(parsed.path).lstrip('/')).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Asset escapes dist directory')
    return path


def http(url, method='GET', headers=None):
    req = urllib.request.Request(url, method=method, headers=headers or {})
    try:
        response = urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        # Small bounded body: enough to reject an HTML fallback and read /health.
        return response.status, dict(response.headers), response.read(65536)


def header(headers, name):
    return next((v for k, v in headers.items() if k.lower() == name.lower()), '')


def javascript_response(status, headers, body):
    mime = header(headers, 'Content-Type').split(';')[0].strip().lower()
    return (status == 200 and mime in ('text/javascript', 'application/javascript', 'application/ecmascript')
            and not body.lstrip().lower().startswith((b'<!doctype html', b'<html')))


def cors_allowed(status, headers, origin):
    origins = header(headers, 'Access-Control-Allow-Origin')
    methods = {m.strip().upper() for m in header(headers, 'Access-Control-Allow-Methods').split(',')}
    allowed_headers = {m.strip().lower() for m in header(headers, 'Access-Control-Allow-Headers').split(',')}
    return (status in (200, 204) and origins in (origin, '*') and 'POST' in methods
            and ('content-type' in allowed_headers or '*' in allowed_headers)
            and header(headers, 'Access-Control-Allow-Credentials').lower() != 'true')


def inspect(dist, worker_asset=None, site_url=None, api_base=None, origin=None, request=http):
    dist = Path(dist).resolve()
    report = {'scope': 'Build artifacts and explicitly requested HTTP checks only',
              'checks': [], 'pending': [], 'files_sha256': {},
              'browser_flow_verified': False, 'demo_ready': False, 'publication_authorized': False}

    def check(name, ok, detail):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})

    index = dist / 'index.html'
    check('index', index.is_file(), str(index))
    assets = []
    if index.is_file():
        parser = Entries()
        parser.feed(index.read_text(encoding='utf-8'))
        check('entry_assets_declared', bool(parser.urls), len(parser.urls))
        for url in parser.urls:
            try:
                path = local_asset(dist, url)
                exists = path.is_file()
                check('entry_asset:' + url, exists, str(path))
                if exists:
                    assets.append(path)
            except ValueError as exc:
                check('entry_asset:' + url, False, str(exc))
    if worker_asset:
        try:
            worker = local_asset(dist, worker_asset)
            exists = worker.is_file() and worker.stat().st_size > 0
            check('worker_asset', exists, str(worker))
            if exists:
                assets.append(worker)
            if site_url:
                url = urllib.parse.urljoin(site_url.rstrip('/') + '/', worker_asset.lstrip('/'))
                try:
                    status, headers, body = request(url)
                    check('worker_http', javascript_response(status, headers, body),
                          {'url': url, 'status': status, 'content_type': header(headers, 'Content-Type')})
                except (OSError, ValueError) as exc:
                    check('worker_http', False, type(exc).__name__)
        except ValueError as exc:
            check('worker_asset', False, str(exc))
    else:
        report['pending'].append('Worker strategy/asset not supplied: browser map readiness is not verified.')
    for path in ([index] if index.is_file() else []) + assets:
        report['files_sha256'][str(path.relative_to(dist))] = hashlib.sha256(path.read_bytes()).hexdigest()
    if api_base:
        try:
            status, headers, body = request(api_base.rstrip('/') + '/health')
            health = json.loads(body)
            check('api_health', status == 200 and health.get('status') == 'ok',
                  {'status': status, 'version': health.get('version'), 'recintos': health.get('recintos')})
        except (OSError, ValueError, AttributeError) as exc:
            check('api_health', False, type(exc).__name__)
        if origin:
            try:
                status, headers, _ = request(api_base.rstrip('/') + '/analyze', method='OPTIONS', headers={
                    'Origin': origin, 'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'content-type'})
                check('api_cors', cors_allowed(status, headers, origin),
                      {'origin': origin, 'status': status, 'allow_origin': header(headers, 'Access-Control-Allow-Origin')})
            except (OSError, ValueError) as exc:
                check('api_cors', False, type(exc).__name__)
        else:
            report['pending'].append('Exact browser origin missing: CORS not verified.')
    else:
        report['pending'].append('API not requested: API health and browser CORS not verified.')
    report['pending'].append('Requires browser test of selection -> API -> result/comparison and labelled fallback.')
    report['passed'] = all(c['ok'] for c in report['checks'])
    return report


def web_url(value):
    url = urllib.parse.urlsplit(value)
    if url.scheme not in ('http', 'https') or not url.netloc or url.username or url.password or url.query or url.fragment:
        raise argparse.ArgumentTypeError('Use an explicit HTTP(S) URL without credentials, query or fragment')
    return value.rstrip('/')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dist', type=Path, required=True, help='Existing production build; never built here')
    ap.add_argument('--worker-asset', help='Explicit dist-relative emitted worker filename; do not guess from file size')
    ap.add_argument('--site-url', type=web_url, help='Existing preview/site URL, including its base path')
    ap.add_argument('--api-base', type=web_url, help='Read-only /health and optional OPTIONS /analyze checks')
    ap.add_argument('--origin', type=web_url, help='Exact browser origin, e.g. http://127.0.0.1:5173')
    args = ap.parse_args()
    if args.site_url and not args.worker_asset:
        ap.error('--site-url requires --worker-asset')
    if args.origin:
        parsed = urllib.parse.urlsplit(args.origin)
        if parsed.path:
            ap.error('--origin must not include a path')
        if not args.api_base:
            ap.error('--origin requires --api-base')
    result = inspect(args.dist, args.worker_asset, args.site_url, args.api_base, args.origin)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
