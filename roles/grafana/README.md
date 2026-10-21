# grafana

Install and configure Grafana dashboards, datasources, and settings.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Run this role only on hosts assigned to its responsibility. Review the defaults and required inputs before rollout.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
grafana_version: latest
grafana_yum_repo_template: grafana.repo.j2
grafana_manage_repo: true
grafana_use_provisioning: true
grafana_provisioning_synced: false
grafana_instance: '{{ ansible_facts.fqdn | default(ansible_host) | default(inventory_hostname) }}'
grafana_logs_dir: /var/log/grafana
grafana_data_dir: /var/lib/grafana
grafana_address: 0.0.0.0
grafana_port: 3000
grafana_cap_net_bind_service: false
grafana_url: http://{{ grafana_address }}:{{ grafana_port }}
grafana_api_url: '{{ grafana_url }}'
grafana_domain: "{{ ansible_facts.fqdn | default(ansible_host) | default('localhost') }}"
grafana_server:
  protocol: http
  enforce_domain: false
  socket: ''
  cert_key: ''
  cert_file: ''
  enable_gzip: false
  static_root_path: public
  router_logging: false
  serve_from_sub_path: false
grafana_security:
  admin_user: admin
  admin_password: ''
grafana_database:
  type: sqlite3
grafana_remote_cache: {}
grafana_welcome_email_on_sign_up: false
grafana_users:
  allow_sign_up: false
  auto_assign_org_role: Viewer
  default_theme: dark
grafana_auth: {}
grafana_ldap: {}
grafana_session: {}
grafana_analytics: {}
grafana_smtp: {}
grafana_alerting:
  execute_alerts: true
grafana_log:
grafana_metrics: {}
grafana_tracing: {}
grafana_snapshots: {}
grafana_image_storage: {}
grafana_plugins: []
grafana_dashboards: []
grafana_dashboards_dir: dashboards
grafana_alert_notifications: []
grafana_datasources: []
grafana_api_keys: []
grafana_api_keys_dir: "{{ lookup('env', 'HOME') }}/grafana/keys"
grafana_environment: {}
grafana_panels: {}
grafana_manage_service: true
grafana_service_enabled: true
grafana_service_state: started
grafana_proxmox_dashboard_enabled: false
```

## Example Playbook

```yaml
- name: Apply grafana
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degit.monitoring.grafana
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

## Native Proxmox dashboard

Set `grafana_proxmox_dashboard_enabled: true` to provision **Proxmox | Native OTLP**
with UID `monitoring-proxmox-native` in the Infrastructure folder. It uses a
separate provider and `monitoring-proxmox` directory below `grafana_data_dir`.
Other dashboard files are untouched. A new/removed provider restarts Grafana when
service management is enabled; JSON updates are picked up every ten seconds.

The 33-panel dashboard adapts Grafana Labs dashboard 23855 revision 1 by spagno.
Source, revision and original SHA256 are recorded beside the asset. It retains the
node/VM/LXC/storage layout and adds tenant/environment/site/cluster/node filters,
metric freshness, missing sources and active cluster alerts. Disk/network rates,
IO-wait and multi-cluster guest table identity are corrected. LXC panels are
expected to be empty when no containers run; an empty active-alert table is healthy.
Select a Prometheus datasource; no external Grafana plugin is required. The
profile needs native PVE metrics processed by the supplied Alloy configuration.
