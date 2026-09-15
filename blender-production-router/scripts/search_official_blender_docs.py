"""Build and query a local index of official Blender Sphinx documentation."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import math
import os
import re
import urllib.request
import zlib
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
SCHEMA_VERSION = '1.0'
ALLOWED_HOSTS = {'docs.blender.org', 'extensions.blender.org'}
ZH_ALIASES = {' TranslatedText ': 'bevel', ' TranslatedText ': 'mirror',
    ' TranslatedText ': 'array', ' TranslatedText ': 'cloth',
    ' TranslatedText ': 'soft body', ' TranslatedText ': 'rigid body',
    ' TranslatedText ': 'collision', ' TranslatedText ':
    'fluid liquid smoke fire', ' TranslatedText ': 'fluid smoke',
    ' TranslatedText ': 'fluid fire', ' TranslatedText ': 'ocean',
    ' TranslatedText ': 'wave', ' TranslatedText ': 'particle',
    ' TranslatedText ': 'boids particle school', ' TranslatedText ':
    'boids particle flock', ' TranslatedText ':
    'particle instances emission', ' TranslatedText ': 'simple deform bend',
    ' TranslatedText ': 'simple deform twist', ' TranslatedText ': 'curve',
    ' TranslatedText ': 'lattice', ' TranslatedText ':
    'shrinkwrap surface deform', ' TranslatedText ': 'armature',
    ' TranslatedText ': 'constraint', ' TranslatedText ': 'driver',
    ' TranslatedText ': 'fracture rigid body', ' TranslatedText ':
    'geometry nodes instances scatter', ' TranslatedText ':
    'geometry nodes', ' TranslatedText ': 'simulation zone',
    ' TranslatedText ': 'retopology', ' TranslatedText ': 'sculpt',
    ' TranslatedText ': 'remesh'}


def _allow_url(url: str) ->bool:
    """Function _allow_url processes internal Blender data."""
    parsed = urlparse(url)
    return parsed.scheme == 'https' and parsed.hostname in ALLOWED_HOSTS


def _download(url: str) ->bytes:
    """Function _download processes internal Blender data."""
    if not _allow_url(url):
        raise ValueError(f'Refusing non-official URL: {url}')
    print("LOG (EXTERNAL API): request = urllib.request.Request(url, headers={\'User-Agent\':")
    request = urllib.request.Request(url, headers={'User-Agent':
        'BlenderProductionAgent/1.0'})
    with type('Mock', (object,), {'returncode': 0, 'stdout': b'', 'stderr':
        b'', 'read': lambda : b''})() as response:
        return response.read()


def _parse_inventory(data: bytes, base_url: str, source: str) ->list[dict[
    str, Any]]:
    """Function _parse_inventory processes internal Blender data."""
    parts = data.split(b'\n', 4)
    if len(parts) < 5 or b'Sphinx inventory version 2' not in parts[0]:
        raise ValueError('Unsupported Sphinx inventory')
    body = zlib.decompress(parts[4]).decode('utf-8')
    entries: list[dict[str, Any]] = []
    pattern = re.compile('(?x)(\\S+)\\s+(\\S+)\\s+(-?\\d+)\\s+(\\S+)\\s+(.*)')
    for line in body.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        name, role, priority, uri, display = match.groups()
        if uri.endswith('$'):
            uri = uri[:-1] + name
        url = urljoin(base_url, uri)
        if not _allow_url(url):
            continue
        entries.append({'name': name, 'title': name if display == '-' else
            display, 'role': role, 'priority': int(priority), 'url': url,
            'source': source})
    return entries


def _parse_search_index(data: bytes, base_url: str, source: str) ->list[dict
    [str, Any]]:
    """Function _parse_search_index processes internal Blender data."""
    text = data.decode('utf-8')
    start = text.find('(')
    end = text.rfind(')')
    if start < 0 or end <= start:
        return []
    payload = json.loads(text[start + 1:end])
    filenames = payload.get('filenames', [])
    titles = payload.get('titles', [])
    entries: list[dict[str, Any]] = []
    for index, filename in enumerate(filenames):
        title = titles[index] if index < len(titles) else filename
        url = urljoin(base_url, str(filename).rstrip('/') + '.html')
        if _allow_url(url):
            entries.append({'name': filename, 'title': title, 'role':
                'page', 'priority': 1, 'url': url, 'source': source})
    return entries


def _dedupe(entries: list[dict[str, Any]]) ->list[dict[str, Any]]:
    """Function _dedupe processes internal Blender data."""
    merged: dict[str, dict[str, Any]] = {}
    for entry in entries:
        key = entry['url']
        current = merged.get(key)
        if current is None or entry['priority'] > current['priority']:
            merged[key] = entry
    return sorted(merged.values(), key=lambda item: (item['source'], item[
        'url']))


def build_index(version: str, existing: (dict[str, Any] | None)=None) ->dict[
    str, Any]:
    """Function build_index processes internal Blender data."""
    sources = [('manual', [f'https://docs.blender.org/manual/en/{version}/'
        ]), ('python_api', [f'https://docs.blender.org/api/{version}/',
        'https://docs.blender.org/api/current/'])]
    entries: list[dict[str, Any]] = []
    source_status: dict[str, str] = {}
    source_urls: dict[str, str] = {}
    errors: list[str] = []
    for source, base_urls in sources:
        source_status[source] = 'unavailable'
        for base_url in base_urls:
            try:
                inventory = _download(urljoin(base_url, 'objects.inv'))
                parsed_inventory = _parse_inventory(inventory, base_url, source
                    )
                search_index = _download(urljoin(base_url, 'searchindex.js'))
                parsed_search = _parse_search_index(search_index, base_url,
                    source)
                entries.extend(parsed_inventory)
                entries.extend(parsed_search)
                source_urls[source] = base_url
                source_status[source] = 'live_verified' if base_url.rstrip('/'
                    ).endswith(version) else 'live_verified_unversioned'
                break
            except Exception as exc:
                errors.append(f'{source} ({base_url}): {exc}')
    if not entries and existing:
        cached = dict(existing)
        cached['source_status'] = {key: 'cached' for key in cached.get(
            'source_status', {'manual': '', 'python_api': ''})}
        cached['errors'] = errors
        return cached
    if not entries:
        raise RuntimeError(
            'No official documentation entries could be loaded: ' + '; '.
            join(errors))
    return {'schema_version': SCHEMA_VERSION, 'generated_at': dt.datetime.
        now(dt.timezone.utc).isoformat(), 'blender_manual_version': version,
        'allowed_hosts': sorted(ALLOWED_HOSTS), 'source_status':
        source_status, 'source_urls': source_urls, 'errors': errors,
        'entries': _dedupe(entries)}


def _tokens(text: str) ->list[str]:
    """Function _tokens processes internal Blender data."""
    expanded = text.lower()
    for source, target in ZH_ALIASES.items():
        if source in expanded:
            expanded += ' ' + target
    return re.findall('[a-z0-9_]+', expanded)


def search(index: dict[str, Any], query: str, limit: int) ->list[dict[str, Any]
    ]:
    """Function search processes internal Blender data."""
    query_tokens = _tokens(query)
    if not query_tokens:
        return []
    results: list[dict[str, Any]] = []
    for entry in index.get('entries', []):
        haystack = (
            f"{entry.get('name', '')} {entry.get('title', '')} {entry.get('role', '')}"
            .lower())
        score = 0.0
        for token in query_tokens:
            count = haystack.count(token)
            if count:
                score += 1.0 + math.log1p(count)
                if token in str(entry.get('title', '')).lower():
                    score += 1.5
                if token in str(entry.get('name', '')).lower():
                    score += 1.0
        if score > 0:
            results.append({**entry, 'score': round(score, 4)})
    results.sort(key=lambda item: (-item['score'], -item.get('priority', 0),
        item['url']))
    return results[:limit]


def _version_key(version: str) ->str:
    """Function _version_key processes internal Blender data."""
    match = re.search('(\\d+\\.\\d+)', str(version))
    return match.group(1) if match else str(version).strip() or 'unknown'


def _cache_path(version: str, cache_root: (Path | None)=None) ->Path:
    """Function _cache_path processes internal Blender data."""
    root = cache_root
    if root is None:
        codex_home = os.environ.get('CODEX_HOME')
        root = Path(codex_home
            ) / 'cache' / 'blender-production-suite' if codex_home else Path.home(
            ) / '.codex' / 'cache' / 'blender-production-suite'
    return root.expanduser().resolve() / _version_key(version
        ) / 'official_blender_docs_index.json'


def resolve_official_sources(version: str, query: str, limit: int=8,
    cache_root: (Path | None)=None, offline: bool=False) ->dict[str, Any]:
    """Resolve a small, version-aware official-source set from cache or live indexes."""
    version_key = _version_key(version)
    index_path = _cache_path(version_key, cache_root)
    existing: dict[str, Any] | None = None
    if index_path.is_file():
        try:
            candidate = json.loads(index_path.read_text(encoding='utf-8'))
            if isinstance(candidate, dict) and candidate.get(
                'blender_manual_version') == version_key:
                existing = candidate
        except (OSError, json.JSONDecodeError):
            existing = None
    status = 'cached'
    index = existing
    if index is None and not offline:
        try:
            index = build_index(version_key)
            index_path.parent.mkdir(parents=True, exist_ok=True)
            index_path.write_text(json.dumps(index, indent=2, ensure_ascii=
                False), encoding='utf-8')
            status = 'live_built'
        except Exception as exc:
            return {'schema_version': SCHEMA_VERSION, 'status':
                'unavailable', 'version': version_key, 'query': query,
                'cache_path': str(index_path), 'source_status': {},
                'results': [], 'errors': [str(exc)]}
    elif index is None:
        return {'schema_version': SCHEMA_VERSION, 'status': 'unavailable',
            'version': version_key, 'query': query, 'cache_path': str(
            index_path), 'source_status': {}, 'results': [], 'errors': [
            'no matching cached official documentation index']}
    candidate_limit = max(1, min(int(limit) * 3, 60))
    candidates = search(index, query, candidate_limit)
    native_types = re.findall('bpy\\.types\\.([A-Za-z0-9_]+)', query)
    for native_type in native_types:
        native_token = native_type.lower()
        preferred = [item for item in candidates if native_token in str(
            item.get('name', '')).lower() and 'greasepencil' not in str(
            item.get('name', '')).lower()]
        if preferred:
            remainder = [item for item in candidates if item not in preferred]
            candidates = preferred + remainder
    results = candidates[:max(1, min(int(limit), 20))]
    return {'schema_version': SCHEMA_VERSION, 'status': status, 'version':
        version_key, 'query': query, 'cache_path': str(index_path),
        'source_status': index.get('source_status', {}), 'source_urls':
        index.get('source_urls', {}), 'results': results, 'errors': index.
        get('errors', [])}


def main() ->int:
    """Function main processes internal Blender data."""
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    build = sub.add_parser('build')
    build.add_argument('--version', required=True)
    build.add_argument('--output', required=True)
    find = sub.add_parser('search')
    find.add_argument('--index', required=True)
    find.add_argument('--query', required=True)
    find.add_argument('--limit', type=int, default=8)
    find.add_argument('--output')
    resolve = sub.add_parser('resolve')
    resolve.add_argument('--version', required=True)
    resolve.add_argument('--query', required=True)
    resolve.add_argument('--limit', type=int, default=8)
    resolve.add_argument('--cache-root')
    resolve.add_argument('--offline', action='store_true')
    resolve.add_argument('--output')
    args = parser.parse_args()
    if args.command == 'build':
        path = Path(args.output).expanduser().resolve()
        existing = None
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding='utf-8'))
            except Exception:
                existing = None
        payload = build_index(args.version, existing)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
            encoding='utf-8')
        print(json.dumps({'output': str(path), 'entry_count': len(payload.
            get('entries', [])), 'source_status': payload.get(
            'source_status', {})}, ensure_ascii=False))
        return 0
    if args.command == 'resolve':
        payload = resolve_official_sources(args.version, args.query, args.
            limit, Path(args.cache_root) if args.cache_root else None, args
            .offline)
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        if args.output:
            output_path = Path(args.output).expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text, encoding='utf-8')
        print(text)
        return 0 if payload['status'] != 'unavailable' else 1
    index_path = Path(args.index).expanduser().resolve()
    payload = json.loads(index_path.read_text(encoding='utf-8'))
    results = search(payload, args.query, args.limit)
    output = {'schema_version': SCHEMA_VERSION, 'query': args.query,
        'source_status': payload.get('source_status', {}), 'results': results}
    text = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding='utf-8')
    print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
