#!/usr/bin/env python3
"""Reject artifacts containing controller dependencies, caches or secrets."""
import hashlib
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
        if (info['namespace'], info['name']) != ('degitag', 'monitoring'):
            raise ValueError('Unexpected collection identity')
        for role in ('alloy', 'node_exporter'):
            if f'roles/{role}/tasks/configuration.yml' not in names:
                raise ValueError(f'Missing transferred role: {role}')
        retired = ('grafana_agent', 'promtail', 'dovecot_exporter', 'ipmi_exporter',
                   'keepalived_exporter', 'postfix_exporter')
        if any(n.startswith(tuple(f'roles/{role}/' for role in retired)) for n in names):
            raise ValueError('Retired or unimplemented role included in artifact')
        verified = set()
        for role in ('ilo5_exporter', 'squid_exporter', 'unbound_exporter'):
            prefix = f'roles/{role}/files/'
            provenance = json.load(archive.extractfile(prefix + 'exporter.provenance.json'))
            if set(provenance['binaries']) != {'amd64', 'arm64'}:
                raise ValueError(f'Missing binary architecture: {role}')
            for arch, expected in provenance['binaries'].items():
                name = prefix + f'{role}_linux_{arch}'
                data = archive.extractfile(name).read()
                if hashlib.sha256(data).hexdigest() != expected:
                    raise ValueError(f'Binary provenance mismatch: {name}')
                verified.add(name)
        for member in archive.getmembers():
            if member.isfile() and archive.extractfile(member).read(4) == b'\x7fELF' and member.name not in verified:
                raise ValueError(f'Unverified bundled executable: {member.name}')
        print(f"Verified {path}: {len(names)} entries, version {info['version']}")


if __name__ == '__main__':
    for argument in sys.argv[1:]:
        check(argument)
