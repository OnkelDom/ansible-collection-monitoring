# loki

Install and configure Grafana Loki.

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
loki_version: 3.3.0
loki_http_listen_port: 3100
loki_http_listen_address: 0.0.0.0
loki_grpc_listen_port: 9096
loki_grpc_listen_address: 127.0.0.1
loki_instance_addr: 127.0.0.1
loki_binary_install_dir: /usr/local/bin
loki_config_dir: /etc/loki
loki_config_file: config.yml
loki_data_dir: /var/lib/loki
loki_rule_path: '{{ loki_data_dir }}/rules'
loki_validate_certs: true
loki_system_user: loki
loki_system_group: loki
loki_auth_enabled: false
loki_log_level: warn
loki_config_extra: {}
loki_config:
  auth_enabled: '{{ loki_auth_enabled }}'
  server:
    http_listen_address: '{{ loki_http_listen_address }}'
    http_listen_port: '{{ loki_http_listen_port }}'
    grpc_listen_address: '{{ loki_grpc_listen_address }}'
    grpc_listen_port: '{{ loki_grpc_listen_port }}'
    log_level: '{{ loki_log_level }}'
  common:
    instance_addr: '{{ loki_instance_addr }}'
    path_prefix: '{{ loki_data_dir }}'
    replication_factor: 1
    ring:
      kvstore:
        store: inmemory
  schema_config:
    configs:
    - from: '2024-01-01'
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
  storage_config:
    filesystem:
      directory: '{{ loki_data_dir }}/chunks'
  ruler:
    alertmanager_url: http://localhost:9093
    storage:
      type: local
      local:
        directory: '{{ loki_data_dir }}/rules'
    rule_path: '{{ loki_rule_path }}'
  analytics:
    reporting_enabled: false
loki_manage_service: true
loki_service_enabled: true
loki_service_state: started
```

## Example Playbook

```yaml
- name: Apply loki
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degit.monitoring.loki
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
