#!/usr/bin/env python3
"""Check bundled LPM rules and real email templates with upstream CLI validators."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]


def plugin(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'plugins/filter' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--promtool', default='promtool')
    parser.add_argument('--amtool', default='amtool')
    parser.add_argument('--output-dir')
    args = parser.parse_args()
    lpm, platform = plugin('monitoring_lpm'), plugin('monitoring_platform')
    source = ROOT / 'roles/prometheus/files/lpm'
    document = lpm.monitoring_lpm_rules(yaml.safe_load((source / 'host.rules').read_text()))
    document = platform.monitoring_platform_annotations(document, yaml.safe_load((source / 'platform-annotations.yml').read_text()))
    with tempfile.TemporaryDirectory(prefix='monitoring-lpm-') as temp:
        folder = Path(temp)
        rules = folder / 'host.rules'
        rules.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True))
        subprocess.run([args.promtool, 'check', 'rules', str(rules)], check=True)
        tests = {'evaluation_interval': '1m', 'tests': []}
        for path in sorted((ROOT / 'tests/lpm').glob('*.test.yml')):
            tests['tests'].extend(yaml.safe_load(path.read_text())['tests'])
        matrix_spec = importlib.util.spec_from_file_location('lpm_matrix', ROOT / 'tests/lpm/matrix_cases.py')
        matrix = importlib.util.module_from_spec(matrix_spec)
        matrix_spec.loader.exec_module(matrix)
        tests['tests'].extend(matrix.matrix_cases())
        print(str(len(tests['tests'])) + ' Promtool source/matrix scenarios', flush=True)
        tests['rule_files'] = [str(rules)]
        suite = folder / 'rules.test.yml'
        suite.write_text(yaml.safe_dump(tests, sort_keys=False, allow_unicode=True))
        subprocess.run([args.promtool, 'test', 'rules', str(suite)], check=True)
        template = ROOT / 'roles/alertmanager/files/monitoring-email.tmpl'
        for path in sorted((ROOT / 'tests/lpm/email').glob('*.json')):
            for part in ['subject', 'text', 'html']:
                output = subprocess.check_output([
                    args.amtool, 'template', 'render', '--template.glob=' + str(template),
                    '--template.text={{ template "monitoring.mail.' + part + '" . }}',
                    '--template.type=' + ('html' if part == 'html' else 'text'),
                    '--template.data=' + str(path)], text=True)
                assert output.strip() and '<no value>' not in output, (path, part)
                assert 'RCW' not in output and 'LenMail' not in output
                if path.stem == 'windows' and part != 'subject':
                    assert 'Get-Volume' in output and 'df -h' not in output
                if path.stem == 'linux' and part != 'subject':
                    assert 'df -h' in output and 'Get-Volume' not in output
                if path.stem == 'escaping' and part == 'html':
                    assert '<script>' not in output and '&lt;script&gt;' in output
                if path.stem == 'resolved' and part == 'subject':
                    assert 'ENTWARNUNG' in output
                if args.output_dir:
                    out = Path(args.output_dir)
                    out.mkdir(parents=True, exist_ok=True)
                    (out / (path.stem + '.' + part)).write_text(output)
            print(path.stem + ': subject, text, HTML OK')


if __name__ == '__main__':
    main()
