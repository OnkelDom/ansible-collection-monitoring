#!/usr/bin/env python3
"""Reject artifacts containing controller dependencies, caches or secrets."""
import json
from pathlib import PurePosixPath
import sys
import tarfile


def check(path):
    with tarfile.open(path, 'r:gz') as archive:
        names = archive.getnames()
        forbidden = {'.venv', '.ansible', '.git', '.pytest_cache', '__pycache__', 'tests', 'tools'}
        invalid = [n for n in names if forbidden.intersection(PurePosixPath(n).parts) or any(p.startswith('.venv') for p in PurePosixPath(n).parts) or n.endswith(('.tar.gz', '.pyc', '.pem', '.key')) or PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts]
        if invalid:
            raise ValueError('Unexpected artifact files: ' + ', '.join(invalid[:10]))
        manifest = json.load(archive.extractfile('MANIFEST.json'))
        info = manifest['collection_info']
        if (info['namespace'], info['name']) != ('degit', 'monitoring'):
            raise ValueError('Unexpected collection identity')
        for role in ('alloy', 'node_exporter'):
            if f'roles/{role}/tasks/configuration.yml' not in names:
                raise ValueError(f'Missing transferred role: {role}')
        if any(n.startswith(('roles/grafana_agent/', 'roles/promtail/')) for n in names):
            raise ValueError('Retired agent included in artifact')
        print(f"Verified {path}: {len(names)} entries, version {info['version']}")


if __name__ == '__main__':
    for argument in sys.argv[1:]:
        check(argument)
