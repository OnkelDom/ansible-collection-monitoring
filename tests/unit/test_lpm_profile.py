from pathlib import Path
import importlib.util
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('lpm', ROOT / 'plugins/filter/monitoring_lpm.py')
lpm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lpm)


def test_bundled_profile_has_no_business_names_or_routing_destinations():
    for path in [*(ROOT / 'roles/prometheus/files/lpm').glob('*'),
                 ROOT / 'roles/alertmanager/files/monitoring-email.tmpl']:
        text = path.read_text().lower()
        for forbidden in ['rcw', 'reifen', 'lenmail', 'dominik', 'jens', 'simon', 'mail_infrastructure', 'pve01']:
            assert forbidden not in text, (path, forbidden)
        assert 'https://' not in text and 'http://' not in text, path


def test_criticality_defaults_preserve_explicit_classification_and_isolation():
    source = yaml.safe_load((ROOT / 'roles/prometheus/files/lpm/host.rules').read_text())
    document = lpm.monitoring_lpm_rules(source)
    for group in document['groups']:
        for rule in group['rules']:
            if 'record' in rule and 'lpm_dsk_criticality' in rule['expr']:
                assert '"mid", "lpm_dsk_criticality", "^$"' in rule['expr']
                assert 'tenant, environment, site' in rule['expr']
    assert source != document
    try:
        lpm.monitoring_lpm_rules(source, 'urgent')
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid criticality was accepted')


def test_email_defaults_preserve_customer_overrides_without_mutating_input():
    routes = [{'config': {'email_configs': [{'to': 'ops@example.invalid'},
               {'html': 'custom', 'headers': {'Subject': 'custom subject'}}]}}]
    result = lpm.monitoring_email_routes(routes)
    email, custom = result[0]['config']['email_configs']
    assert 'monitoring.mail.html' in email['html']
    assert 'monitoring.mail.subject' in email['headers']['Subject']
    assert custom['html'] == 'custom' and custom['headers']['Subject'] == 'custom subject'
    assert 'html' not in routes[0]['config']['email_configs'][0]
    assert lpm.monitoring_email_routes(routes, False) == routes


def test_filesystem_alias_exclusions_are_exact_and_preserve_canonical_mounts():
    import re
    import importlib.util
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location('alias_filter', root / 'plugins/filter/monitoring_lpm.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expression = module.monitoring_filesystem_mount_exclude('^/(dev|proc|run|sys)($|/)', ['/var/lib/app.test', '/var/lib/app.test'])
    assert re.search(expression, '/var/lib/app.test')
    assert not re.search(expression, '/var/lib/appXtest')
    assert not re.search(expression, '/var/lib/app.test/cache')
    assert not re.search(expression, '/opt/app')
    assert re.search(expression, '/run/credentials/test')
    assert expression.count('^/var/lib/') == 1
    for invalid in [['/'], ['relative'], ['/var/lib/app/'], 'not-a-list']:
        import pytest
        with pytest.raises(ValueError):
            module.monitoring_filesystem_mount_exclude('', invalid)
