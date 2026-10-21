"""Prepare the bundled, vendor-neutral host monitoring profile."""
from copy import deepcopy
import re


def monitoring_lpm_rules(document, criticality='mid', dashboard_url='', runbook_url=''):
    if criticality not in ('high', 'mid', 'low'):
        raise ValueError('LPM criticality must be high, mid or low')
    result = deepcopy(document)
    for group in result['groups']:
        for rule in group['rules']:
            if 'record' in rule:
                labels = set(re.findall(r'\blpm_\w+_criticality\b', rule['expr']))
                for label in sorted(labels):
                    rule['expr'] = (f'label_replace(({rule["expr"]}), "{label}", '
                                    f'"{criticality}", "{label}", "^$")')
            else:
                for name, value in [('dashboard_url', dashboard_url), ('runbook_url', runbook_url)]:
                    if value:
                        rule['annotations'][name] = value
    return result


class FilterModule:
    def filters(self):
        return {'monitoring_lpm_rules': monitoring_lpm_rules, 'monitoring_email_routes': monitoring_email_routes,
                'monitoring_filesystem_mount_exclude': monitoring_filesystem_mount_exclude}


def monitoring_email_routes(routes, enabled=True):
    result = deepcopy(routes)
    if enabled:
        defaults = {
            'html': '{{ template "monitoring.mail.html" . }}',
            'text': '{{ template "monitoring.mail.text" . }}',
        }
        for route in result:
            for email in route.get('config', {}).get('email_configs', []):
                for name, value in defaults.items():
                    email.setdefault(name, value)
                email.setdefault('headers', {}).setdefault('Subject', '{{ template "monitoring.mail.subject" . }}')
    return result


def monitoring_filesystem_mount_exclude(base, aliases=None):
    """Exclude explicit mount aliases exactly; never merge all mounts by device."""
    if not isinstance(base, str):
        raise ValueError('The filesystem base exclusion must be a regex string')
    aliases = [] if aliases is None else aliases
    if not isinstance(aliases, list) or any(not isinstance(p, str) or not p.startswith('/') or p == '/' or p.endswith('/') for p in aliases):
        raise ValueError('Mount aliases must be absolute non-root paths without trailing slash')
    parts = [base] if base else []
    parts.extend('^' + re.escape(path) + '$' for path in sorted(set(aliases)))
    return '|'.join(parts)
