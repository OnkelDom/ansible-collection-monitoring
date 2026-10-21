# alloy

Install and configure Grafana Alloy as a telemetry agent.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9
- Windows (Alloy agent only; separate runtime validation required)

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Owned exclusively by degit.monitoring. Optional firewall rules delegate to degit.infrastructure.firewall. Configure only one telemetry agent for each metric source.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
alloy_manage_repository: true
alloy_manage_service: true
alloy_service_enabled: true
alloy_service_state: started
alloy_repository_url: https://apt.grafana.com
alloy_repository_key_url: https://apt.grafana.com/gpg-full.key
alloy_repository_keyring: /etc/apt/keyrings/grafana.asc
alloy_config_file: '{{ alloy_config_dir }}/config.alloy'
alloy_user: alloy
alloy_group: alloy
alloy_log_level: info
alloy_loki_endpoint: ''
alloy_normal_logs_tenant: logs
alloy_audit_logs_tenant: audit
alloy_config:
  logging:
    level: '{{ alloy_log_level }}'
    format: logfmt
alloy_custom_blocks: []
alloy_custom_blocks_group_vars: []
alloy_custom_blocks_host_vars: []
alloy_custom_blocks_playbook: []
alloy_manage_firewall: false
alloy_firewall_enabled: false
alloy_firewall_zone: public
alloy_manage_selinux: true
alloy_firewall_ports: []
alloy_selinux_ports: '{{ alloy_firewall_ports }}'
alloy_service_override: {}
alloy_linux_install_package: true
alloy_windows_install_method: existing
alloy_windows_installer_url: ''
alloy_windows_installer_path: C:/Windows/Temp/alloy-installer-windows-amd64.exe
alloy_windows_product_id: GrafanaLabs.Alloy
alloy_windows_binary_path: C:/Program Files/GrafanaLabs/Alloy/alloy-windows-amd64.exe
alloy_config_dir: "{{ _alloy_platform_config_dir | default('/etc/alloy') }}"
alloy_data_dir: "{{ _alloy_platform_data_dir | default('/var/lib/alloy') }}"
alloy_validate_config: true
alloy_labels:
  tenant: default
  environment: prod
  site: default
  platform: generic
  system_role: server
  component_type: compute
  managed_by: ansible
alloy_loki_tenant_id: ''
alloy_loki_external_labels: {}
alloy_prometheus_remote_write_url: ''
alloy_prometheus_remote_write_headers: {}
alloy_prometheus_external_labels: {}
alloy_linux_metrics_enabled: true
alloy_linux_metrics_collectors_disabled: []
alloy_linux_metrics_collectors_enabled: []
alloy_linux_metrics_textfile_directory: ''
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
- memory
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
alloy_pipeline_enabled: false
alloy_windows_installer_checksum: ''
alloy_binary_path: "{{ _alloy_platform_binary_path | default('/usr/bin/alloy') }}"
alloy_package_name: "{{ _alloy_platform_package_name | default('alloy') }}"
alloy_service_name: "{{ _alloy_platform_service_name | default('alloy') }}"
alloy_log_dir: "{{ _alloy_platform_log_dir | default('/var/log/alloy') }}"
alloy_selinux_packages: '{{ _alloy_platform_selinux_packages | default([]) }}'
alloy_selinux_port_type: "{{ _alloy_platform_selinux_port_type | default('http_port_t') }}"
alloy_rpm_repository_url: https://rpm.grafana.com
alloy_rpm_repository_key_url: https://rpm.grafana.com/gpg.key
alloy_lpm_enabled: true
alloy_proxmox_enabled: false
alloy_proxmox_endpoint: 127.0.0.1:14318
alloy_proxmox_htpasswd_file: ''
alloy_proxmox_tls_cert_file: ''
alloy_proxmox_tls_key_file: ''
alloy_proxmox_remote_write_url: ''
alloy_proxmox_remote_write_headers: {}
alloy_proxmox_labels:
  tenant: default
  environment: prod
  site: default
alloy_linux_filesystem_mount_points_exclude: ^/(dev|proc|run|sys)($|/)
alloy_linux_filesystem_mount_points_exclude_extra: []
```

## Example Playbook

```yaml
- name: Apply alloy
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degit.monitoring.alloy
```

## Testing

Build and install the current collection checkout before running syntax checks, so the
fully qualified role reference resolves to this implementation.

Run `python tools/generate_role_scaffold.py --check`, `pytest tests/unit` and
`bash tests/run_role_syntax_checks.sh` from the collection root.
CI additionally runs YAML lint, Ansible lint, collection build/install and container smoke tests.
VM functional results are tracked separately; metadata lists intended compatibility,
not proof that every feature has passed on every distribution.

## Dependencies

Install the collection dependencies from `requirements.yml`. Role dependencies:
`[]`.

## Change management

Use check mode where the underlying modules support it. Review the diff before applying
changes. Network, firewall, identity and storage changes need an out-of-band recovery
path. Secrets belong in Ansible Vault or the operator secret store, never in defaults.

## Ownership

This role is owned exclusively by `degit.monitoring`. Host firewall policy remains in `degit.infrastructure`.

## Native Proxmox OTLP receiver

Set `alloy_proxmox_enabled: true` on the central Linux receiver. This feature is
independent of the local host pipeline and uses its own remote-write component.
`alloy_proxmox_remote_write_url` must point to the Prometheus write receiver.
The default listener `127.0.0.1:14318` is intended behind a TLS reverse proxy;
14318 avoids an existing Tempo listener on 4318. Route exactly `/v1/metrics`.
Use `alloy_proxmox_htpasswd_file` with a high-entropy per-environment credential.
An externally bound listener requires both TLS certificate/key and htpasswd.
Never disable PVE certificate verification. Secrets stay in private files/Vault.

`alloy_proxmox_labels` assigns trusted tenant/environment/site labels at the
receiver. All sources sharing this receiver must belong to that same trust domain.
Separate customers/environments need separate authenticated receiver instances or
components, not client-supplied tenant labels. Cluster/node identity comes from
PVE resource attributes; `monitoring.cluster` supplies the globally unique cluster
name, including on standalone PVE. Guest identity includes tenant, environment,
site, cluster and VMID; migration does not change that identity. Local receiver
host labels and the host LPM profile are never added to PVE metrics.

Metric unit suffix inference is disabled deliberately: native PVE already names
counters, and inferred units vary across field names. The supplied rules and
dashboard consume stable raw `proxmox_*` names. Existing dashboards using
`*_bytes` or `*_seconds` must be adapted and must not be mixed into this profile.

For adopting an existing Linux Alloy pipeline, `tasks_from: proxmox_receiver`
validates and adds only a marked block. The full role renders the same marked
block. Set enabled false to remove it. The scoped task preserves existing source
and log pipelines; reapply it after any older baseline that replaces config.alloy.
No extra agent is required on PVE for this native metric export. Local Alloy and
Node Exporter remain responsible for journal/crash logs and detailed OS metrics.

## Filesystem aliases and bind mounts

Use `alloy_linux_filesystem_mount_points_exclude_extra` for audited bind-mount
aliases whose capacity is already monitored at a canonical mount. The list is
empty by default and contains absolute exact mount paths. The collection escapes
regex characters and anchors each alias; an independently mounted descendant is
preserved. `/` and ambiguous trailing slashes are rejected. Never deduplicate all
mounts solely by device: Btrfs subvolumes, quotas and independent mounts can have
different capacity semantics. Keep at least one canonical mount per filesystem.
Excluding an alias removes both byte and inode duplicates while canonical LPM
capacity alerts remain unchanged. Stale historical samples expire normally.
Legacy custom Alloy blocks must explicitly consume the same variables; the
structured pipeline applies them automatically. No customer paths are defaults.
