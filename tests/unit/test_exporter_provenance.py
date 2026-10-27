"""Protect the release boundary around bundled executables."""
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]


def test_bundled_exporters_have_verified_architecture_and_source_locks():
    for role in ('ilo5_exporter', 'squid_exporter', 'unbound_exporter'):
        files = ROOT / 'roles' / role / 'files'
        provenance = json.loads((files / 'exporter.provenance.json').read_text())
        assert len(provenance['revision']) == 40
        assert provenance['source_url'].endswith(provenance['revision'])
        assert provenance['cgo_enabled'] == '0'
        for name in ('go.mod', 'go.sum'):
            lock = ROOT / 'tools/exporters' / role / name
            assert hashlib.sha256(lock.read_bytes()).hexdigest() == provenance[name + '_sha256']
        for arch, machine in (('amd64', 62), ('arm64', 183)):
            binary = (files / f'{role}_linux_{arch}').read_bytes()
            assert binary[:6] == b'\x7fELF\x02\x01'
            assert struct.unpack_from('<H', binary, 18)[0] == machine
            assert hashlib.sha256(binary).hexdigest() == provenance['binaries'][arch]


def test_unimplemented_roles_are_excluded_from_release():
    for role in ('dovecot_exporter', 'ipmi_exporter', 'keepalived_exporter', 'postfix_exporter'):
        assert not (ROOT / 'roles' / role).exists()
