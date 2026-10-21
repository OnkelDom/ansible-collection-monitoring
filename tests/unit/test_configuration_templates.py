from pathlib import Path

from ansible.plugins.filter.core import FilterModule
from jinja2 import Environment, StrictUndefined
import yaml
import importlib.util


ROOT = Path(__file__).resolve().parents[2]


def render(relative, **variables):
    environment = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    environment.filters.update(FilterModule().filters())
    spec = importlib.util.spec_from_file_location('monitoring_lpm', ROOT / 'plugins/filter/monitoring_lpm.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    environment.filters.update({'degit.monitoring.' + k: v for k, v in module.FilterModule().filters().items()})
    return environment.from_string((ROOT / relative).read_text()).render(**variables)


def test_alertmanager_renders_typed_smtp_and_nested_routes():
    text = render(
        'roles/alertmanager/templates/alertmanager.config.j2',
        ansible_managed='Managed by Ansible', alertmanager_resolve_timeout='5m',
        alertmanager_lpm_enabled=True, alertmanager_lpm_inhibit_rules=[],
        alertmanager_smtp={'require_tls': False, 'smarthost': 'localhost:25'},
        alertmanager_time_intervals=[], alertmanager_inhibit_rules=[],
        alertmanager_config_dir='/etc/alertmanager',
        alertmanager_route={'receiver': 'blackhole', 'group_by': ['alertname']},
        alertmanager_routes=[{'receiver': 'mail', 'config': {
            'email_configs': [{'to': 'monitoring@example.invalid', 'send_resolved': True}]},
            'routes': [{'matchers': ['severity="critical"'], 'continue': False}]}],
    )
    config = yaml.safe_load(text)
    assert config['global']['smtp_require_tls'] is False
    assert config['receivers'][1]['email_configs'][0]['send_resolved'] is True
    assert config['route']['routes'][0]['receiver'] == 'mail'
    assert config['route']['routes'][0]['continue'] is False


def test_loki_merges_extra_settings_without_losing_base_configuration():
    text = render('roles/loki/templates/loki.config.yml.j2',
                  loki_config={'server': {'http_listen_port': 3100}, 'auth_enabled': False},
                  loki_config_extra={'server': {'grpc_listen_port': 9096}})
    config = yaml.safe_load(text)
    assert config['server'] == {'http_listen_port': 3100, 'grpc_listen_port': 9096}
    assert config['auth_enabled'] is False
