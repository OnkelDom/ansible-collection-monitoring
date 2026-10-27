#!/usr/bin/env python3
"""Exercise the shipped inhibition policy against a real isolated Alertmanager."""
import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

import yaml

ROOT = Path(__file__).resolve().parents[1]


def cases():
    base = dict(instance='source-independent-host', tenant='tenant-a', environment='lab',
                site='site-a', platform='linux', category='io', name='sda',
                alert_family='LPMDiskAwaitHigh', lpm='high', monitoring_profile='lpm')
    alerts = []
    expected = {}

    def add(case, labels, severity='WARN', suppressed=False):
        labels = dict(labels, alertname=case, severity=severity, validation_case=case)
        alerts.append({'labels': labels})
        if severity == 'WARN' or case.startswith('down-target'):
            expected[case] = suppressed

    add('source-error', base, 'ERROR')
    add('matching-resource', base, suppressed=True)
    # These are operator boundaries, independent of the implementation's equal list.
    for label in ('instance', 'tenant', 'environment', 'site', 'platform', 'category',
                  'name', 'device', 'path', 'interface', 'target', 'server', 'port',
                  'protocol', 'method', 'alert_family', 'lpm', 'monitoring_profile'):
        add('different-' + label, dict(base, **{label: 'different'}))
    no_instance = dict(base)
    no_instance.pop('instance')
    add('missing-instance-source', no_instance, 'ERROR')
    add('missing-instance-target', no_instance)
    down = dict(base, instance='down-host', category='availability', alert_family='LPMCollectorDown')
    add('collector-down', down, 'ERROR')
    target = dict(base, instance='down-host')
    add('down-target-warn', target, suppressed=True)
    add('down-target-error', target, 'ERROR', suppressed=True)
    add('down-target-other-platform', dict(target, platform='windows'))
    add('down-target-other-tenant', dict(target, tenant='other'))
    add('down-target-availability', dict(target, category='availability'))
    return alerts, expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--alertmanager', required=True)
    args = parser.parse_args()
    defaults = yaml.safe_load((ROOT / 'roles/alertmanager/defaults/main.yml').read_text())
    config = {'route': {'receiver': 'blackhole', 'group_wait': '1s', 'group_interval': '1s'},
              'receivers': [{'name': 'blackhole'}],
              'inhibit_rules': deepcopy(defaults['alertmanager_lpm_inhibit_rules'])}
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    base_url = f'http://127.0.0.1:{port}'
    with tempfile.TemporaryDirectory(prefix='lpm-inhibition-') as directory:
        folder = Path(directory)
        config_path = folder / 'alertmanager.yml'
        config_path.write_text(yaml.safe_dump(config, sort_keys=False))
        with (folder / 'runtime.log').open('w+') as log:
            process = subprocess.Popen([
                str(Path(args.alertmanager).resolve()), '--config.file=' + str(config_path),
                f'--web.listen-address=127.0.0.1:{port}', '--cluster.listen-address=',
                '--storage.path=' + str(folder / 'data')], stdout=log, stderr=log)
            try:
                for _ in range(100):
                    try:
                        with urllib.request.urlopen(base_url + '/-/ready', timeout=1):
                            break
                    except (OSError, urllib.error.URLError):
                        if process.poll() is not None:
                            raise RuntimeError('Isolated Alertmanager exited before readiness')
                        time.sleep(.1)
                else:
                    raise RuntimeError('Isolated Alertmanager did not become ready')
                alerts, expected = cases()
                now = datetime.now(timezone.utc)
                for alert in alerts:
                    alert['startsAt'] = (now - timedelta(minutes=1)).isoformat()
                    alert['endsAt'] = (now + timedelta(minutes=5)).isoformat()
                request = urllib.request.Request(base_url + '/api/v2/alerts',
                                                 data=json.dumps(alerts).encode(),
                                                 headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(request, timeout=5):
                    pass
                mismatches = {}
                for _ in range(100):
                    with urllib.request.urlopen(base_url + '/api/v2/alerts', timeout=5) as response:
                        actual = {alert['labels']['validation_case']: bool(alert['status']['inhibitedBy'])
                                  for alert in json.load(response)}
                    mismatches = {case: (wanted, actual.get(case)) for case, wanted in expected.items()
                                  if actual.get(case) != wanted}
                    if not mismatches:
                        break
                    time.sleep(.1)
                if mismatches:
                    raise AssertionError(f'Inhibition boundary failures: {mismatches}')
                print(f'{len(expected)} real Alertmanager inhibition cases passed; blackhole only')
            except BaseException:
                log.flush()
                log.seek(0)
                print(log.read()[-4000:])
                raise
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == '__main__':
    main()
