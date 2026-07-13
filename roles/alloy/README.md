# alloy

Install and configure Grafana Alloy as a telemetry agent.

## Supported platforms

- Ubuntu 22.04+
- Debian 12+
- RHEL 9+

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
alloy_service_enabled: true
alloy_service_state: started
alloy_linux_install_package: true
alloy_windows_install_method: winget
alloy_windows_installer_url: ''
alloy_windows_installer_path: C:/Windows/Temp/alloy-installer-windows-amd64.exe
alloy_windows_product_id: GrafanaLabs.Alloy
alloy_windows_binary_path: C:/Program Files/GrafanaLabs/Alloy/alloy.exe
alloy_config_file: ''
alloy_config_dir: ''
alloy_data_dir: ''
alloy_user: alloy
alloy_group: alloy
alloy_log_level: info
alloy_validate_config: true
alloy_labels:
  tenant: default
  environment: prod
  site: default
  platform: generic
  system_role: server
  component_type: compute
  managed_by: ansible
alloy_loki_endpoint: ''
alloy_loki_tenant_id: ''
alloy_loki_external_labels: {}
alloy_prometheus_remote_write_url: ''
alloy_prometheus_remote_write_headers: {}
alloy_prometheus_external_labels: {}
alloy_linux_metrics_enabled: true
alloy_linux_metrics_collectors_disabled: []
alloy_linux_metrics_collectors_enabled: []
alloy_linux_metrics_textfile_directory: /var/lib/prometheus/node-exporter
alloy_linux_journal_enabled: true
alloy_linux_journal_max_age: 24h
alloy_linux_file_logs_enabled: true
alloy_linux_file_log_targets:
- path: /var/log/syslog
  job: syslog
  log_type: system
  service: syslog
- path: /var/log/messages
  job: messages
  log_type: system
  service: messages
- path: /var/log/auth.log
  job: auth
  log_type: security
  service: auth
- path: /var/log/secure
  job: secure
  log_type: security
  service: secure
- path: /var/log/audit/audit.log
  job: audit
  log_type: security
  service: audit
alloy_windows_metrics_enabled: true
alloy_windows_enabled_collectors:
- cpu
- cs
- logical_disk
- net
- os
- service
- system
alloy_windows_eventlog_enabled: true
alloy_windows_eventlogs:
- name: Application
  job: windows-eventlog-application
  log_type: application
  service: application
- name: System
  job: windows-eventlog-system
  log_type: system
  service: system
- name: Security
  job: windows-eventlog-security
  log_type: security
  service: security
alloy_windows_bookmark_dir: C:/ProgramData/GrafanaLabs/Alloy/bookmarks
alloy_extra_config: ''
alloy_firewall_enabled: false
alloy_firewall_ports: []
alloy_service_override: {}
```

Wenn `alloy_loki_endpoint` leer ist, wird kein Logversand konfiguriert. Wenn `alloy_prometheus_remote_write_url` leer ist, wird kein Metrikversand konfiguriert.

`alloy_linux_metrics_textfile_directory` bindet vorhandene `*.prom`-Dateien in den Linux-Metrikpfad ein, zum Beispiel fuer SMART-, NVMe- oder applikationsnahe Textfile-Collector. Die Rolle legt nur das Verzeichnis an und konfiguriert Alloy; Erzeugung, Timer und Paketquellen der Textfile-Dateien bleiben separate Host-Integrationen.

## Linux-Beispiel

```yaml
- name: Apply alloy
  hosts: all
  become: true
  roles:
    - role: lenmail.monitoring.alloy
```

## Testing

The collection CI runs `ansible-lint`, `ansible-test sanity`, repository consistency tests, and per-role syntax checks using `roles/alloy/tests/test.yml`.
