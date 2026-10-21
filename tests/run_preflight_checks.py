#!/usr/bin/env python3
"""Exercise installed preflights with synthetic facts, never installation tasks.

This checks platform selection, negative cases and input precedence. It does not
establish service compatibility on the named operating systems.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    cases = [('debian13', 'Debian', 'Debian', '13'),
             ('ubuntu22', 'Ubuntu', 'Debian', '22.04'),
             ('ubuntu24', 'Ubuntu', 'Debian', '24.04'),
             ('ubuntu26', 'Ubuntu', 'Debian', '26.04'),
             ('rocky9', 'Rocky', 'RedHat', '9'),
             ('rhel9', 'RedHat', 'RedHat', '9'),
             ('windows', 'Microsoft Windows Server 2022', 'Windows', '10.0'),
             ('unsupported', 'Ubuntu', 'Debian', '18.04'),
             ('unimplemented', 'Debian', 'Debian', '13')]
    hosts = {}
    for name, distribution, family, version in cases:
        path = 'C:/Managed/Alloy' if family == 'Windows' else '/tmp/preflight-only-alloy'
        roles = ['alloy', 'node_exporter', 'prometheus']
        if family == 'Windows':
            roles = ['alloy']
        if name == 'unimplemented':
            roles = ['postfix_exporter']
        hosts[name] = {
            'ansible_connection': 'local', 'ansible_python_interpreter': os.sys.executable,
            'monitoring_test_facts': {'distribution': distribution, 'os_family': family,
                              'distribution_version': version,
                              'distribution_major_version': version.split('.')[0],
                              'architecture': 'x86_64', 'hostname': name,
                              'selinux': {'status': 'disabled'}, 'mounts': [], 'interfaces': [], 'processor_count': 1, 'processor_vcpus': 2, 'domain': 'example.invalid', 'pkg_mgr': 'apt' if family == 'Debian' else 'dnf'},
            'alloy_config_dir': path, 'monitoring_test_config_dir': path,
            'monitoring_test_roles': roles,
            'monitoring_test_expect_failure': name in ('unsupported', 'unimplemented')}
    with tempfile.TemporaryDirectory(prefix='monitoring-preflight-') as directory:
        inventory = Path(directory) / 'inventory.json'
        inventory.write_text(json.dumps({'all': {'hosts': hosts}}))
        subprocess.run(['ansible-playbook', '-i', str(inventory),
                        str(Path(__file__).parent / 'integration/preflight.yml')], check=True)


if __name__ == '__main__':
    main()
