# prometheus

Install and configure the Prometheus server and rule files.

## Supported platforms

- Ubuntu 22.04+
- Debian 12+
- RHEL 9+

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
proxy_env: {}
prometheus_version: 2.48.0
prometheus_web_external_url: https://prometheus.{{ ansible_external_domain }}
prometheus_webconfig: {}
prometheus_log_level: warn
prometheus_storage_retention_time: 30d
prometheus_remote_write_reveicer: true
prometheus_config_flags_extra: {}
prometheus_config: "{{ all_prometheus_config|default({}) | combine(group_vars_prometheus_config|default({}),recursive=True,list_merge='append') | combine(host_vars_prometheus_config|default({}),recursive=True,list_merge='append') | combine(defaults_prometheus_config|default({}),recursive=True,list_merge='append') }}"
prometheus_static_targets_files: '{{ all_prometheus_static_targets_files|default([]) + group_vars_prometheus_static_targets_files|default([]) + host_vars_prometheus_static_targets_files|default([]) }}'
prometheus_alert_rules_files: '{{ all_prometheus_alert_rules_files|default([]) + group_vars_prometheus_alert_rules_files|default([]) + host_vars_prometheus_alert_rules_files|default([]) }}'
prometheus_alert_rules_src_dir: prometheus/rules
prometheus_static_targets_src_dir: prometheus/file_sd
defaults_prometheus_config:
  global:
    scrape_interval: 60s
    scrape_timeout: 10s
  rule_files:
  - /etc/prometheus/rules/*.rules
```

## Example Playbook

```yaml
- name: Apply prometheus
  hosts: all
  become: true
  roles:
    - role: lenmail.monitoring.prometheus
```

## Testing

The collection CI runs `ansible-lint`, `ansible-test sanity`, repository consistency tests, and per-role syntax checks using `roles/prometheus/tests/test.yml`.
