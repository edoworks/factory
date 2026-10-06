#!/usr/bin/env python3
"""One-command clean generation and executed verification; no dependencies installed."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def main(destination):
    started = time.monotonic()
    root = Path(destination).absolute()
    if root != root.resolve() or root.exists() or not root.parent.is_dir() or ROOT in root.parents:
        raise ValueError('Benchmark destination must be a new canonical path outside the factory')
    lock = json.loads((ROOT / 'toolchain.json').read_text())
    node, chrome = os.environ.get('FACTORY_NODE'), os.environ.get('FACTORY_CHROME')
    if not node or not chrome or not Path(chrome).is_file():
        raise ValueError('Set FACTORY_NODE and FACTORY_CHROME to existing executables')
    if platform.python_version() != lock['python']:
        raise ValueError('Python differs from toolchain lock')
    if subprocess.check_output([node, '--version'], text=True).strip() != 'v' + lock['node']:
        raise ValueError('Node differs from toolchain lock')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, timeout=15):
        raise ValueError('Commit the complete source before running this pinned benchmark')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    root.mkdir()
    receipt = {'status': 'running', 'factory_revision': revision, 'toolchain': lock,
               'paid_api_calls': 0, 'paid_provisioning': False, 'manual_output_patches': 0,
               'checks': [], 'scope': 'generated local web core; native/AI/backend qualification excluded'}

    def run(name, args, cwd=ROOT, timeout=90):
        start = time.monotonic()
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        (root / (name + '.log')).write_text(result.stdout + result.stderr)
        receipt['checks'].append({'name': name, 'exit_code': result.returncode, 'seconds': round(time.monotonic() - start, 4)})
        if result.returncode:
            raise RuntimeError(name + ' failed; see its log')
        return result.stdout

    try:
        run('generator-tests', [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v'])
        with tempfile.TemporaryDirectory(prefix='factory-source-closure-') as tmp:
            isolated = Path(tmp).resolve(); runtime = isolated / 'runtime'; runtime.mkdir()
            (runtime / 'templates').mkdir()
            for name in ['factory.py', 'toolchain.json']:
                shutil.copyfile(ROOT / name, runtime / name)
            for path in (ROOT / 'templates').iterdir():
                if path.is_file(): shutil.copyfile(path, runtime / 'templates' / path.name)
            spec = json.loads((ROOT / 'specs/couch-clash.json').read_text())
            spec_path = isolated / 'product-spec.json'; spec_path.write_text(json.dumps(spec))
            for name in ['app', 'regenerated']:
                run('generate-' + name, [sys.executable, '-B', str(ROOT / 'tests/isolated_generate.py'), str(runtime), str(spec_path), str(root / name), revision], cwd=isolated, timeout=10)
            files = {p.name: p.read_bytes() for p in (root / 'app').iterdir()}
            if files != {p.name: p.read_bytes() for p in (root / 'regenerated').iterdir()}:
                raise AssertionError('Deterministic regeneration differs')
            receipt['deterministic_files'] = sorted(files)
            changed = copy.deepcopy(spec)
            changed['id'] = 'alternate-rivalry'; changed['title'] = 'Another Rivalry'
            changed['questions'][0]['text'] = 'Which side opens the scoring?'
            changed['questions'][0]['points'] = 333
            spec_path.write_text(json.dumps(changed))
            run('generate-variant', [sys.executable, '-B', str(ROOT / 'tests/isolated_generate.py'), str(runtime), str(spec_path), str(root / 'variant'), revision], cwd=isolated, timeout=10)
        for name in ['app', 'variant']:
            run('engine-' + name, [node, '--test', str(root / name / 'engine.test.mjs')])
            run('browser-' + name, [node, str(ROOT / 'tests/browser.mjs'), str(root / name)])
        receipt['status'] = 'passed'
        receipt['artifact_sha256'] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in sorted(root.rglob('*')) if p.is_file()}
    except Exception as exc:
        receipt['status'] = 'failed'; receipt['error'] = str(exc)
        raise
    finally:
        receipt['seconds'] = round(time.monotonic() - started, 4)
        receipt['retained_bytes'] = sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
        if receipt['seconds'] > 120 or receipt['retained_bytes'] > 100 * 1024 * 1024:
            receipt['status'] = 'failed'; receipt['error'] = 'Benchmark operating limit exceeded'
        (root / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps(receipt, indent=2))
    if receipt['status'] != 'passed':
        raise RuntimeError(receipt.get('error', 'Benchmark failed'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    main(parser.parse_args().out)
