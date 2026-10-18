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
prometheus_data_dir: /var/lib/prometheus
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
prometheus_platform_annotation_overrides: []
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

## Technical operating-system alarm content

LPM rules are currently supplied by the infrastructure repository through
`prometheus_alert_rules_files` and `prometheus_alert_rules_src_dir`. This collection
does not ship its own LPM rule set; the role validates and installs the supplied
files without rewriting their annotations.

For CPU, RAM, disk, network and service alarms, use technical annotations:

- `summary`: resource, host and the observed condition; avoid vague terms such as
  “Speicherdruck”, “IO-Problem” or “Verarbeitung beeinträchtigt”.
- `description`: measured value, unit, aggregation window, threshold and required
  duration. Describe every relevant condition in a combined expression.
- `action`: platform-specific diagnostic commands and the next operational step.
- `impact`: optional; omit generic consequences that add no information.
- `resolved_action`: optional explanation of what the ended alarm proves and
  which service check remains. Consumers must explicitly support this annotation.

Only report a cause established by a metric or a detected error. Missing exporter
metrics do not establish that the monitored application is unavailable. A stale
textfile does not establish a write-permission error.

Include available bytes and total capacity when the measurement provides them.
Keep current measurements separate from historical averages. Optional annotation
queries must handle absent results without template errors. For SQL, use
“SQL-Abfrage” for SELECT queries, “SQL-Datenänderung” for INSERT/UPDATE/DELETE and
“SQL-Ausführung” when the alert covers multiple statement types.

Before deployment, run `promtool check rules`, rule tests covering the rendered
annotations, and notification-template previews. Content-only changes must leave
expressions, thresholds, evaluation durations and routing labels unchanged.

Platform variants are compiled with `prometheus_platform_annotation_overrides`; see
[the filter contract](../../plugins/README.md). Select the monitored platform,
never the Prometheus host OS, and provide a neutral fallback for absent labels.
