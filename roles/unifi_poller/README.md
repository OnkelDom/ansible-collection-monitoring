# unifi_poller

Install and configure the Unifi Poller metrics exporter.

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
proxy_env: {}
unifi_poller_version: 2.1.3
unifi_poller_system_user: unifi-poller
unifi_poller_system_group: unifi-poller
unifi_poller_binary_install_dir: /usr/local/bin
unifi_poller_binary_name: unpoller
unifi_poller_config_path: /etc/unifi-poller
unifi_poller_config_file: config.yaml
unifi_poller_service_name: unifi-poller
unifi_poller_manage_service: true
unifi_poller_service_enabled: true
unifi_poller_service_state: started
unifi_poller_config:
  poller:
    quiet: false
    debug: false
    plugins: []
  prometheus:
    disable: false
    http_listen: 0.0.0.0:9130
    ssl_cert_path: ''
    ssl_key_path: ''
    report_errors: false
  loki:
    url: http://localhost:3100/api/v1/push
    user: ''
    pass: ''
    verify_ssl: false
    tenant_id: ''
    interval: 2m
    timeout: 10s
  influxdb:
    disable: false
    interval: 30s
    url: http://127.0.0.1:8086
    user: ''
    pass: ''
    db: ''
    verify_ssl: false
    dead_ports: false
  webserver:
    enable: false
    port: 37288
    html_path: '{{ unifi_poller_config_path }}/web'
    ssl_cert_path: ''
    ssl_key_path: ''
    max_events: 200
    accounts: {}
  unifi:
    dynamic: false
    defaults:
      url: https://127.0.0.1:8443
      user: ''
      pass: ''
      sites:
      - all
      save_ids: false
      save_events: false
      save_alarms: false
      save_anomalies: false
      save_dpi: false
      save_sites: true
      hash_pii: false
      verify_ssl: false
    controllers:
    - url: https://127.0.0.1:8443
      user: ''
      pass: ''
      sites:
      - all
      save_ids: false
      save_events: false
      save_alarms: false
      save_anomalies: false
      save_dpi: false
      save_sites: true
      hash_pii: false
      verify_ssl: false
```

## Example Playbook

```yaml
- name: Apply unifi_poller
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degit.monitoring.unifi_poller
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
