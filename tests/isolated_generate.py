"""Audit-constrained generation, not an OS security boundary for hostile Python."""
import importlib.util
import json
import os
import socket
from pathlib import Path
import sys

runtime, spec, out, revision = sys.argv[1:5]
target = sys.argv[5] if len(sys.argv) == 6 else 'web'
runtime, spec, out = Path(runtime).resolve(), Path(spec).resolve(), Path(out).resolve()
loader = importlib.util.spec_from_file_location('fresh_factory', runtime / 'factory.py')
factory = importlib.util.module_from_spec(loader)
loader.loader.exec_module(factory)
allowed_reads = {runtime / 'factory.py', runtime / 'toolchain.json', spec}
allowed_reads.update(runtime / 'templates' / name for name in factory.TEMPLATES)
if target == 'ios':
    allowed_reads.update(runtime / 'templates/ios' / name for name in factory.IOS_TEMPLATES)
seen = set()


def audit(event, args):
    if event == 'open' and not isinstance(args[0], int):
        target = Path(args[0]).resolve()
        mode, flags = args[1], args[2]
        writing = flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
        if writing:
            if out.parent not in target.parents:
                raise PermissionError('Generator write outside owned output parent')
        elif target not in allowed_reads:
            raise PermissionError('Generator read outside declared source/spec closure')
        else:
            seen.add(str(target.relative_to(runtime)) if runtime in target.parents else 'product-spec.json')
    if event.startswith(('socket.', 'subprocess.', 'ctypes.')) or event in ('os.system', 'os.exec', 'os.posix_spawn'):
        raise PermissionError('Generator network/process/native-code access forbidden')


sys.addaudithook(audit)
try:
    Path('/etc/hosts').read_bytes()
    raise AssertionError('Undeclared read probe unexpectedly passed')
except PermissionError:
    pass
try:
    socket.socket()
    raise AssertionError('Network probe unexpectedly passed')
except PermissionError:
    pass
manifest = factory.generate(spec, out, revision, target)
print(json.dumps({'status': 'generated', 'audit': 'undeclared read and network probes rejected',
                  'observed_reads': sorted(seen), 'spec_sha256': manifest['spec_sha256']}))
