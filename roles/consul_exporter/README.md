# consul_exporter

Install and configure the Prometheus consul_exporter.

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
consul_exporter_version: 0.7.1
consul_exporter_web_listen_address: 0.0.0.0
consul_exporter_web_listen_port: 9107
consul_exporter_log_level: warn
consul_exporter_log_format: json
consul_exporter_binary_install_dir: /usr/local/bin
consul_exporter_system_user: consul_exporter
consul_exporter_system_group: consul_exporter
consul_exporter_consul_token: ''
consul_exporter_params:
- consul.server=localhost:8500
consul_exporter_manage_service: true
consul_exporter_service_enabled: true
consul_exporter_service_state: started
```

## Example Playbook

```yaml
- name: Apply consul_exporter
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.monitoring.consul_exporter
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
