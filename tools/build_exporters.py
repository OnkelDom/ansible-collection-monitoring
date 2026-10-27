#!/usr/bin/env python3
"""Rebuild bundled Linux exporters from checksum-pinned sources and module locks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify shipped binaries without rebuilding')
    parser.add_argument('--update', action='store_true', help='Record hashes after an intentional source/toolchain update')
    args = parser.parse_args()
    for manifest in sorted(ROOT.glob('roles/*/files/exporter.provenance.json')):
        info = json.loads(manifest.read_text())
        role = manifest.parents[1].name
        lock = ROOT / 'tools/exporters' / role
        for name in ('go.mod', 'go.sum'):
            if digest(lock / name) != info[name + '_sha256']:
                raise ValueError(f'{role}: modified dependency lock {name}')
        patch = lock / 'compatibility.patch'
        if patch.exists() and digest(patch) != info.get('patch_sha256'):
            raise ValueError(f'{role}: modified source patch')
        if info.get('patch_sha256') and not patch.exists():
            raise ValueError(f'{role}: missing source patch')
        if args.check:
            if set(info['binaries']) != {'amd64', 'arm64'}:
                raise ValueError(f'{role}: missing architecture')
            for arch, expected in info['binaries'].items():
                if digest(manifest.parent / f'{role}_linux_{arch}') != expected:
                    raise ValueError(f'{role}: invalid {arch} binary')
            print(f'{role}: verified source locks and binary hashes')
            continue
        version = subprocess.check_output(['go', 'env', 'GOVERSION'], text=True).strip()
        if version != info['go_version']:
            raise ValueError(f"Build requires {info['go_version']}, found {version}")
        with tempfile.TemporaryDirectory(prefix=f'{role}-build-') as directory:
            archive = Path(directory) / 'source.tar.gz'
            urllib.request.urlretrieve(info['source_url'], archive)
            if digest(archive) != info['source_sha256']:
                raise ValueError(f'{role}: source checksum mismatch')
            source_root = Path(directory) / 'source'
            source_root.mkdir()
            with tarfile.open(archive) as source_archive:
                source_archive.extractall(source_root, filter='data')
            source = next(source_root.iterdir())
            patch = lock / 'compatibility.patch'
            if patch.exists():
                if digest(patch) != info['patch_sha256']:
                    raise ValueError(f'{role}: patch checksum mismatch')
                subprocess.run(['patch', '-p0', '-i', str(patch)], cwd=source, check=True)
            for name in ('go.mod', 'go.sum'):
                shutil.copyfile(lock / name, source / name)
            if info.get('test_pattern'):
                native_env = dict(os.environ, CGO_ENABLED='0', GOTOOLCHAIN='local')
                native_env.pop('GOOS', None)
                native_env.pop('GOARCH', None)
                subprocess.run(['go', 'test', '-mod=readonly', '-run', info['test_pattern'], info.get('test_package', '.')],
                               cwd=source, env=native_env, check=True)
            env = dict(os.environ, CGO_ENABLED='0', GOOS='linux', GOTOOLCHAIN='local')
            subprocess.run(['go', 'mod', 'verify'], cwd=source, env=env, check=True)
            for arch in ('amd64', 'arm64'):
                output = Path(directory) / f'{role}_linux_{arch}'
                subprocess.run(['go', 'build', *info['build_flags'], '-o', str(output), '.'],
                               cwd=source, env=dict(env, GOARCH=arch), check=True)
                checksum = digest(output)
                if not args.update and info['binaries'].get(arch) != checksum:
                    raise ValueError(f'{role}: non-reproducible {arch} build')
                shutil.copyfile(output, manifest.parent / output.name)
                info['binaries'][arch] = checksum
            if args.update:
                manifest.write_text(json.dumps(info, indent=2) + '\n')
        print(f'{role}: rebuilt both Linux architectures')


if __name__ == '__main__':
    main()
