"""Materialize and verify the exact committed inputs used by a benchmark."""
import hashlib
import io
from pathlib import Path, PurePosixPath
import subprocess
import tarfile


def verify_snapshot(root, identity):
    root = Path(root)
    actual = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
    if actual != identity['files'] or any(p.is_symlink() for p in root.rglob('*')):
        raise ValueError('Committed source snapshot content mismatch')


def capture_snapshot(repo, destination, revision):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args], timeout=15)
    if git('rev-parse', 'HEAD').decode().strip() != revision:
        raise ValueError('Requested revision does not match source HEAD')
    if git('status', '--porcelain'):
        raise ValueError('Source checkout is dirty')
    tree = git('rev-parse', revision + '^{tree}').decode().strip()
    archive = git('archive', '--format=tar', revision)
    contents = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as source:
        for member in source.getmembers():
            name = PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts or member.issym() or member.islnk():
                raise ValueError('Unsafe committed source archive')
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError('Unsupported source archive entry')
            contents[str(name)] = source.extractfile(member).read()
    dest = Path(destination)
    dest.mkdir()  # New private directory only; never replace an existing checkout.
    for name, data in contents.items():
        path = dest / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    identity = {'status': 'verified_committed_snapshot', 'commit': revision, 'tree': tree,
                'archive_sha256': hashlib.sha256(archive).hexdigest(),
                'files': {name: hashlib.sha256(data).hexdigest() for name, data in sorted(contents.items())}}
    verify_snapshot(dest, identity)
    return identity
