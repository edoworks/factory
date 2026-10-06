#!/usr/bin/env python3
"""Original offline spec compiler. Reads only its declared source closure and spec."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
TEMPLATES = ('index.html', 'style.css', 'engine.mjs', 'app.mjs', 'engine.test.mjs')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected), 'Unknown or missing fields')


def label(value):
    require(type(value) is str and 0 < len(value.strip()) <= 160, 'Invalid text')
    require(not any(ord(c) < 32 for c in value), 'Control characters are forbidden')


def identifier(value):
    require(type(value) is str and re.fullmatch(r'[a-z][a-z0-9-]{0,39}', value), 'Invalid ID')
    require(value not in ('skip', 'void', 'constructor', 'prototype', '__proto__'), 'Reserved ID')


def validate(spec):
    keys(spec, ('schema_version', 'id', 'title', 'description', 'assets', 'questions', 'stages'))
    require(type(spec['schema_version']) is int and spec['schema_version'] == 1, 'Unsupported spec version')
    identifier(spec['id']); label(spec['title']); label(spec['description'])
    require(spec['assets'] == [], 'This version supports original CSS and text only; assets must be empty')
    require(type(spec['questions']) is list and 1 <= len(spec['questions']) <= 12, 'Question limit')
    question_ids = set()
    for q in spec['questions']:
        keys(q, ('id', 'text', 'scope', 'points', 'options'))
        identifier(q['id']); label(q['text']); label(q['scope'])
        require(q['id'] not in question_ids, 'Duplicate question')
        question_ids.add(q['id'])
        require(type(q['points']) is int and 1 <= q['points'] <= 10000, 'Invalid points')
        require(type(q['options']) is list and 2 <= len(q['options']) <= 8, 'Option limit')
        ids = set()
        for option in q['options']:
            keys(option, ('id', 'label')); identifier(option['id']); label(option['label'])
            require(option['id'] not in ids, 'Duplicate option'); ids.add(option['id'])
    require(type(spec['stages']) is list and 2 <= len(spec['stages']) <= 8, 'Stage limit')
    locked, revealed, stages = set(), set(), set()
    for stage in spec['stages']:
        keys(stage, ('id', 'title', 'kind', 'questions', 'boost'))
        identifier(stage['id']); label(stage['title'])
        require(stage['id'] not in stages, 'Duplicate stage'); stages.add(stage['id'])
        require(stage['kind'] in ('lock', 'reveal') and type(stage['boost']) is bool, 'Invalid stage kind')
        ids = stage['questions']
        require(type(ids) is list and 1 <= len(ids) <= 12 and all(type(i) is str for i in ids), 'Invalid stage questions')
        require(len(ids) == len(set(ids)) and set(ids) <= question_ids, 'Unknown/duplicate stage question')
        if stage['kind'] == 'lock':
            require(not set(ids) & locked and len(ids) <= 3, 'Question locked twice or too many prompts')
            locked.update(ids)
        else:
            require(not stage['boost'] and set(ids) <= locked and not set(ids) & revealed, 'Invalid reveal ordering')
            revealed.update(ids)
    require(locked == revealed == question_ids, 'Every question must be locked and revealed exactly once')
    return spec


def generate(spec_path, destination, revision):
    require(re.fullmatch(r'[0-9a-f]{40}', revision), 'Exact factory revision required')
    source_bytes = Path(spec_path).read_bytes()
    require(len(source_bytes) <= 32768, 'Spec size limit')
    spec = validate(json.loads(source_bytes))
    dest = Path(destination).absolute()
    require('..' not in Path(destination).parts, 'Traversal output forbidden')
    require(dest == dest.resolve() and dest != ROOT and ROOT not in dest.parents, 'Unsafe output path')
    require(dest.parent.is_dir() and dest.name not in ('', '.', '..'), 'Output parent must exist')
    require(not dest.exists() or (dest.is_dir() and not any(dest.iterdir())), 'Output must be empty')
    toolchain = json.loads((ROOT / 'toolchain.json').read_text())
    require(platform.python_version() == toolchain['python'], 'Python version differs from toolchain lock')
    canonical = json.dumps(spec, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
    spec_sha = digest(canonical)
    files = {name: (ROOT / 'templates' / name).read_bytes() for name in TEMPLATES}
    files['spec.mjs'] = ('export const fingerprint = ' + json.dumps(spec_sha) + ';\nexport const spec = ' + canonical.decode() + ';\n').encode()
    closure = {'factory.py': digest(Path(__file__).read_bytes()), 'toolchain.json': digest((ROOT / 'toolchain.json').read_bytes())}
    closure.update({'templates/' + name: digest(files[name]) for name in TEMPLATES})
    manifest = {'schema_version': 1, 'factory_repository': 'edoworks/factory', 'factory_revision': revision,
                'revision_status': 'caller_supplied_unverified',
                'source_closure': closure, 'spec_sha256': spec_sha, 'toolchain': toolchain,
                'assets': [], 'network_source_reads': False, 'product_source_reuse': False,
                'files': {name: digest(data) for name, data in sorted(files.items())}}
    files['manifest.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    require(sum(map(len, files.values())) <= 5 * 1024 * 1024, 'Output size limit')
    scratch = Path(tempfile.mkdtemp(prefix='.factory-generate-', dir=dest.parent))
    try:
        for name, data in files.items():
            (scratch / name).write_bytes(data)
        # rename refuses a nonempty destination that appeared after preflight.
        os.rename(scratch, dest)
    finally:
        if scratch.exists():
            shutil.rmtree(scratch)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--revision', required=True)
    args = parser.parse_args()
    try:
        result = generate(args.spec, args.out, args.revision)
        print(json.dumps({'status': 'generated', 'spec_sha256': result['spec_sha256'], 'files': len(result['files']) + 1}))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({'status': 'rejected', 'error': str(exc)}), file=sys.stderr)
        sys.exit(1)
