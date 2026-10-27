# node_exporter

Install and configure Prometheus node_exporter.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Owned exclusively by degitag.monitoring. Optional firewall rules delegate to degitag.infrastructure.firewall. Configure only one telemetry agent for each metric source.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
proxy_env: {}
node_exporter_version: 1.12.1
node_exporter_web_listen_address: 0.0.0.0
node_exporter_binary_install_dir: /usr/local/bin
node_exporter_binary_path: '{{ node_exporter_binary_install_dir }}/node_exporter'
node_exporter_web_listen_port: 9100
node_exporter_manage_service: true
node_exporter_service_enabled: true
node_exporter_service_state: started
node_exporter_manage_firewall: false
node_exporter_firewall_zone: public
node_exporter_manage_selinux: true
node_exporter_firewall_ports:
- '{{ node_exporter_web_listen_port }}/tcp'
node_exporter_selinux_ports: '{{ node_exporter_firewall_ports }}'
node_exporter_system_user: node_exporter
node_exporter_system_group: node_exporter
node_exporter_user_additional_groups: adm
node_exporter_create_consul_agent_service: false
node_exporter_textfile_dir: /var/lib/node_exporter
node_exporter_config_dir: /etc/node_exporter
node_exporter_log_level: warn
node_exporter_log_format: json
node_exporter_disable_go_metrics: true
node_exporter_textfile_collectors: []
node_exporter_tls_server_config: {}
node_exporter_http_server_config: {}
node_exporter_basic_auth_users: {}
node_exporter_enabled_collectors:
- filesystem:
    mount-points-exclude: ^/(boot|boot/efi|dev.+|proc|run|run.+|sys.+|var/lib/docker.+|var/lib/containers/storage.+)($|/)$
- textfile:
    directory: '{{ node_exporter_textfile_dir }}'
node_exporter_disabled_collectors:
- bonding
- zfs
- btrfs
- infiniband
- edac
- nfs
- nfsd
- xfs
- entropy
- rapl
node_exporter_webconfig: []
node_exporter_checksum: ''
```

## Example Playbook

```yaml
- name: Apply node_exporter
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.monitoring.node_exporter
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

This role is owned exclusively by `degitag.monitoring`. Host firewall policy remains in `degitag.infrastructure`.
