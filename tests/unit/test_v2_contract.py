from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def tasks(document):
    for task in document or []:
        if not isinstance(task, dict):
            continue
        yield task
        for key in ('block', 'rescue', 'always'):
            yield from tasks(task.get(key))


def test_service_handlers_honour_explicit_management_and_stop_state():
    for path in (ROOT / 'roles').glob('*/handlers/*.yml'):
        for task in tasks(yaml.safe_load(path.read_text())):
            key = next((key for key in task if key.split('.')[-1] in (
                'service', 'systemd', 'systemd_service', 'win_service')), None)
            if key is None:
                continue
            conditions = str(task.get('when', ''))
            assert '_service_policy.manage' in conditions, (path, task['name'])
            if task[key].get('state') in ('restarted', 'reloaded', 'started'):
                assert "_service_policy.state" in conditions and "!= 'stopped'" in conditions, (path, task['name'])


def test_agent_platform_defaults_do_not_shadow_inventory_values():
    paths = (ROOT / 'roles/alloy/vars/platform').glob('*.yml')
    for path in paths:
        variables = yaml.safe_load(path.read_text()) or {}
        assert all(name.startswith('_alloy_platform_') for name in variables), path


def test_windows_configuration_is_staged_and_validated_before_activation():
    document = yaml.safe_load((ROOT / 'roles/alloy/tasks/windows.yml').read_text())
    names = [task['name'] for task in document]
    assert names.index('Validate the Windows installation contract') == 0
    assert names.index('Validate alloy configuration') < names.index('Activate the validated Windows Alloy configuration')
    staged = next(task for task in document if task['name'] == 'Generate alloy configuration file')
    assert staged['ansible.windows.win_template']['dest'].endswith('.candidate')
    download = next(task for task in document if task['name'] == 'Download Grafana Alloy installer')
    assert download['ansible.windows.win_get_url']['checksum_algorithm'] == 'sha256'


def test_blackbox_defaults_have_no_customer_targets_or_active_post_probes():
    path = ROOT / 'roles/blackbox_exporter/defaults/main.yml'
    text = path.read_text()
    assert 'reifen-wolf' not in text and 'lenmail.de' not in text
    assert 'POST' not in text


def test_native_services_use_requested_state_and_enablement():
    services = {
        'prometheus': 'prometheus', 'alertmanager': 'alertmanager',
        'blackbox_exporter': 'blackbox_exporter', 'loki': 'loki',
        'node_exporter': 'node_exporter', 'tempo': 'tempo',
    }
    for role, service in services.items():
        path = ROOT / 'roles' / role / 'tasks/configuration.yml'
        managed = [task[key] for task in tasks(yaml.safe_load(path.read_text()))
                   for key in ('ansible.builtin.systemd', 'ansible.builtin.systemd_service')
                   if key in task and task[key].get('name') == service
                   and 'state' in task[key]]
        assert managed, role
        for config in managed:
            assert config['state'] == '{{ ' + role + '_service_state }}', role
            assert config['enabled'] == '{{ ' + role + '_service_enabled }}', role
