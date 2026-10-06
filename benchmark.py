#!/usr/bin/env python3
"""One-command clean generation and executed verification; no dependencies installed."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
from snapshot import capture_snapshot, verify_snapshot

ROOT = Path(__file__).resolve().parent


def validate_accounting(value):
    if value['schema_version'] != 1 or value['assistant_percent'] != 100 or value['factory_percent'] != 0:
        raise ValueError('Accounting baseline remains 100% assistant / 0% factory')
    if value['work_units'] != ['spec-validation', 'generation', 'deterministic-regeneration', 'executed-tests', 'artifact-and-review-package']:
        raise ValueError('Accounting work-unit coverage changed')
    if any(value[key] is not None for key in ('active_assistant_seconds', 'active_human_seconds', 'tokens', 'dollars')):
        raise ValueError('Unmeasured labor or cost must remain unknown')


def validate_receipt_metrics(value):
    if 'paid_api_calls' in value or 'paid_provisioning' in value:
        raise ValueError('Paid-service limits are declared constraints, not measured usage')
    if value['declared_run_constraints'] != {'source': 'declared_constraint', 'paid_api_calls_allowed': 0, 'paid_provisioning_allowed': False}:
        raise ValueError('Run constraints must be explicitly labelled')
    if value['manual_output_patches'] is not None or any(value['run_observation'][key] is not None for key in ('assistant_interventions_during_command', 'manual_output_edits')):
        raise ValueError('Unmeasured edits and interventions must remain unknown')
    if 'executor_report' in value and value['executor_report'].get('source') != 'executor_report':
        raise ValueError('Executor assertions must identify their source')


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
               'declared_run_constraints': {'source': 'declared_constraint', 'paid_api_calls_allowed': 0, 'paid_provisioning_allowed': False},
               'manual_output_patches': None,
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
        with tempfile.TemporaryDirectory(prefix='factory-source-closure-') as tmp:
            isolated = Path(tmp).resolve(); runtime = isolated / 'runtime'
            identity = capture_snapshot(ROOT, runtime, revision)
            receipt['source_identity'] = identity
            if (runtime / 'benchmark.py').read_bytes() != (ROOT / 'benchmark.py').read_bytes():
                raise ValueError('Benchmark runner differs from committed snapshot')
            receipt['accounting_baseline'] = json.loads((runtime / 'autonomy-baseline.json').read_text())
            validate_accounting(receipt['accounting_baseline'])
            run('generator-tests', [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v'], cwd=runtime)
            spec = json.loads((runtime / 'specs/couch-clash.json').read_text())
            spec_path = isolated / 'product-spec.json'; spec_path.write_text(json.dumps(spec))
            for name in ['app', 'regenerated']:
                run('generate-' + name, [sys.executable, '-B', str(runtime / 'tests/isolated_generate.py'), str(runtime), str(spec_path), str(root / name), revision], cwd=isolated, timeout=10)
            files = {p.name: p.read_bytes() for p in (root / 'app').iterdir()}
            if files != {p.name: p.read_bytes() for p in (root / 'regenerated').iterdir()}:
                raise AssertionError('Deterministic regeneration differs')
            receipt['deterministic_files'] = sorted(files)
            changed = copy.deepcopy(spec)
            changed['id'] = 'alternate-rivalry'; changed['title'] = 'Another Rivalry'
            changed['questions'][0]['text'] = 'Which side opens the scoring?'
            changed['questions'][0]['points'] = 333
            spec_path.write_text(json.dumps(changed))
            run('generate-variant', [sys.executable, '-B', str(runtime / 'tests/isolated_generate.py'), str(runtime), str(spec_path), str(root / 'variant'), revision], cwd=isolated, timeout=10)
            collision = copy.deepcopy(spec); old_id = collision['questions'][0]['id']
            collision['questions'][0]['id'] = 'boost'
            for stage in collision['stages']:
                stage['questions'] = ['boost' if q == old_id else q for q in stage['questions']]
            spec_path.write_text(json.dumps(collision))
            run('generate-id-collision', [sys.executable, '-B', str(runtime / 'tests/isolated_generate.py'), str(runtime), str(spec_path), str(root / 'id-collision'), revision], cwd=isolated, timeout=10)
            receipt['spec_identities'] = {}
            for name in ['app', 'variant', 'id-collision']:
                manifest = json.loads((root / name / 'manifest.json').read_text())
                for source, digest in manifest['source_closure'].items():
                    if identity['files'].get(source) != digest:
                        raise ValueError('Generated provenance differs from committed source')
                receipt['spec_identities'][name] = manifest['spec_sha256']
                run('engine-' + name, [node, '--test', str(root / name / 'engine.test.mjs')], cwd=runtime)
                run('browser-' + name, [node, str(runtime / 'tests/browser.mjs'), str(root / name)], cwd=runtime)
            verify_snapshot(runtime, identity)
            receipt['source_identity']['verified_after_run'] = True
        receipt['status'] = 'passed'
        receipt['artifact_sha256'] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in sorted(root.rglob('*')) if p.is_file()}
    except Exception as exc:
        receipt['status'] = 'failed'; receipt['error'] = str(exc)
        raise
    finally:
        receipt['seconds'] = round(time.monotonic() - started, 4)
        receipt['run_observation'] = {'wall_seconds': receipt['seconds'], 'assistant_interventions_during_command': None,
                                      'intervention_scope': 'interventions and edits are not instrumented; development/setup/review labor also unmeasured',
                                      'manual_output_edits': None, 'active_assistant_seconds': None, 'active_human_seconds': None,
                                      'tokens': None, 'dollars': None,
                                      'factory_run_stages': ['spec validation', 'generation', 'deterministic regeneration', 'tests', 'artifact collection'],
                                      'assistant_manual_stages': ['invocation/setup', 'source review-package transfer', 'independent review coordination'],
                                      'required_approvals': 'external to runner; no approval is inferred from a passing test'}
        receipt['retained_bytes'] = sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
        if receipt['seconds'] > 120 or receipt['retained_bytes'] > 100 * 1024 * 1024:
            receipt['status'] = 'failed'; receipt['error'] = 'Benchmark operating limit exceeded'
        receipt['run_observation']['quality_gate'] = receipt['status']
        validate_receipt_metrics(receipt)
        (root / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps(receipt, indent=2))
    if receipt['status'] != 'passed':
        raise RuntimeError(receipt.get('error', 'Benchmark failed'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    main(parser.parse_args().out)
