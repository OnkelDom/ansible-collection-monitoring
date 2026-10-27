#!/usr/bin/env python3
"""Download checksum-verified upstream CLI validators for the collection tests."""
import argparse
import hashlib
from pathlib import Path
import platform
import shutil
import sys
import tarfile
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', required=True)
    args = parser.parse_args()
    root = Path(args.dest).resolve()
    root.mkdir(parents=True, exist_ok=True)
    system = {'darwin': 'darwin', 'linux': 'linux'}[sys.platform]
    arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'amd64'}[platform.machine()]
    for project, version, binary in [('prometheus', '2.48.0', 'promtool'), ('alertmanager', '0.27.0', 'amtool')]:
        name = f'{project}-{version}.{system}-{arch}.tar.gz'
        base = f'https://github.com/prometheus/{project}/releases/download/v{version}/'
        sums = urllib.request.urlopen(base + 'sha256sums.txt').read().decode()
        digest = next(line.split()[0] for line in sums.splitlines() if line.split()[-1].lstrip('*') == name)
        archive = root / name
        if not archive.exists():
            urllib.request.urlretrieve(base + name, archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
            raise ValueError('Upstream checksum mismatch: ' + name)
        with tarfile.open(archive) as handle:
            for executable in ([binary, 'alertmanager'] if project == 'alertmanager' else [binary]):
                member = handle.getmember(name.removesuffix('.tar.gz') + '/' + executable)
                with handle.extractfile(member) as source, (root / executable).open('wb') as target:
                    shutil.copyfileobj(source, target)
                (root / executable).chmod(0o755)
        print(binary + ' ' + version + ': upstream SHA256 verified')


if __name__ == '__main__':
    main()
