#!/usr/bin/env python3
"""Semantic native PVE rule checks; no network or mail delivery."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from ansible.plugins.filter.core import FilterModule

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='monitoring-proxmox-check-') as directory:
    work = Path(directory)
    env = Environment(loader=FileSystemLoader(ROOT / 'roles/prometheus/templates'), undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.filters.update(FilterModule().filters())
    values = yaml.safe_load((ROOT / 'roles/prometheus/defaults/main.yml').read_text())
    identity = dict(tenant='validation', environment='lab', site='lab', cluster='cluster-a')
    values.update(prometheus_proxmox_expected_nodes=[identity | dict(node='pve')], prometheus_proxmox_expected_guests=[identity | dict(vmid='999')])
    (work / 'native.rules').write_text(env.get_template('proxmox.rules.j2').render(**values))
    shutil.copy(ROOT / 'tests/proxmox/rules.test.yml', work / 'rules.test.yml')
    tool = os.environ.get('PROMTOOL', 'promtool')
    subprocess.run([tool, 'check', 'rules', 'native.rules'], cwd=work, check=True)
    subprocess.run([tool, 'test', 'rules', 'rules.test.yml'], cwd=work, check=True)
