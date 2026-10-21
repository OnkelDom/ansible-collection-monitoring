import json
from pathlib import Path

from ansible.plugins.filter.core import FilterModule
from jinja2 import Environment, FileSystemLoader, StrictUndefined
import yaml

ROOT = Path(__file__).resolve().parents[2]


def render(role, template, **extra):
    env = Environment(loader=FileSystemLoader(ROOT / 'roles' / role / 'templates'),
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.filters.update(FilterModule().filters())
    values = yaml.safe_load((ROOT / 'roles' / role / 'defaults/main.yml').read_text())
    return env.get_template(template).render(**(values | extra))


def test_expected_nodes_are_explicit_and_guests_are_opt_in():
    data = yaml.safe_load(render('prometheus', 'proxmox.rules.j2',
                                prometheus_proxmox_expected_nodes=[dict(tenant='one', environment='prod', site='west', cluster='a', node='pve')]))
    expected = data['groups'][0]['rules'][0]
    assert expected['labels']['instance'] == 'a/pve'
    alerts = data['groups'][1]['rules']
    assert len(alerts) == 7
    assert all('action' in r['annotations'] for r in alerts)
    assert 'ProxmoxNativeExpectedGuestMissing' not in [r['alert'] for r in alerts]
    assert 'memavailable' in next(r['expr'] for r in alerts if r['alert'] == 'ProxmoxNativeMemoryHigh')


def test_receiver_uses_source_identity_and_separate_remote_write():
    text = render('alloy', 'proxmox-otlp.alloy.j2', alloy_proxmox_remote_write_url='http://localhost/write')
    assert 'resource.attributes["proxmox.node"]' in text
    assert 'resource.attributes["monitoring.cluster"]' in text
    assert 'prometheus.remote_write.proxmox.receiver' in text
    assert 'prometheus.remote_write.default.receiver' not in text
    assert 'external_labels' not in text
    assert 'guest_id' in text
    assert 'add_metric_suffixes = false' in text


def test_dashboard_has_scoped_queries_and_source_attribution():
    dashboard = json.loads((ROOT / 'roles/grafana/files/dashboards/proxmox-native.json').read_text())
    assert len(dashboard['panels']) == 33
    assert dashboard['links'][0]['url'].endswith('23855-proxmox-ve-dashboard/')
    for panel in dashboard['panels']:
        for target in panel.get('targets', []):
            expression = target.get('expr', '')
            for label in ['tenant', 'environment', 'site', 'cluster', 'node']:
                assert (panel['id'] == 104 and label == 'node') or f'{label}=~"${label}"' in expression, (panel['title'], label)
            assert '${DS_PROMETHEUS}' not in str(target)
    assert 'joinByField' in str(dashboard)
    assert "'byField': 'guest_id'" in str(dashboard)
