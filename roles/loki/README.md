# loki

Install and configure Grafana Loki.

## Supported platforms

- Ubuntu 22.04+
- Debian 12+
- RHEL 9+

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
loki_config:
  auth_enabled: '{{ loki_auth_enabled }}'
  server:
    http_listen_address: '{{ loki_http_listen_address }}'
    http_listen_port: '{{ loki_http_listen_port }}'
    grpc_listen_address: '{{ loki_grpc_listen_address }}'
    grpc_listen_port: '{{ loki_grpc_listen_port }}'
    log_level: '{{ loki_log_level }}'
  common:
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
```

## Example Playbook

```yaml
- name: Apply loki
  hosts: all
  become: true
  roles:
    - role: lenmail.monitoring.loki
```

## Testing

The collection CI runs `ansible-lint`, `ansible-test sanity`, repository consistency tests, and per-role syntax checks using `roles/loki/tests/test.yml`.
