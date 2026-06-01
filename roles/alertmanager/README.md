# alertmanager

Install and configure Prometheus Alertmanager.

## Supported platforms

- Ubuntu 22.04+
- Debian 12+
- RHEL 9+

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
proxy_env: {}
alertmanager_version: 0.27.0
alertmanager_log_level: warn
alertmanager_webconfig: {}
alertmanager_config_dir: /etc/alertmanager
alertmanager_web_external_url: https://alertmanager.{{ alertmanager_external_domain }}
alertmanager_template_files: []
alertmanager_template_src_dir: alertmanager
alertmanager_config_flags_extra: {}
alertmanager_cluster: {}
alertmanager_resolve_timeout: 5m
alertmanager_smtp: {}
alertmanager_time_intervals: []
alertmanager_inhibit_rules: []
alertmanager_route:
  receiver: blackhole
  group_by:
  - alertname
  repeat_interval: 4h
  group_interval: 5m
alertmanager_routes: []
alertmanager_config: "{{ all_alertmanager_config|default({}) | combine(group_vars_alertmanager_config|default({}),recursive=True,list_merge='append') | combine(host_vars_alertmanager_config|default({}),recursive=True,list_merge='append') | combine(defaults_alertmanager_config|default({}),recursive=True,list_merge='append') }}"
```

## Example Playbook

```yaml
- name: Apply alertmanager
  hosts: all
  become: true
  roles:
    - role: lenmail.monitoring.alertmanager
```

## Testing

The collection CI runs `ansible-lint`, `ansible-test sanity`, repository consistency tests, and per-role syntax checks using `roles/alertmanager/tests/test.yml`.
