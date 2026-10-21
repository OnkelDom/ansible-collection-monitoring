# vector

Install and configure Vector for log and metric pipelines.

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
vector_prepare: true
vector_install: true
vector_configure: true
vector_service: true
vector_configure_rm_default: true
vector_configure_config_path: /etc/vector/vector.yaml
vector_configure_data_dir: /var/lib/vector
vector_configure_api:
  enabled: true
vector_configure_sources:
  syslog:
    type: syslog
    address: 0.0.0.0:514
    max_length: '102_400'
    mode: udp
    path: /tmp/syslog_udp
vector_configure_sinks:
  loki:
    type: loki
    inputs:
    - source_syslog
    endpoint: http://localhost:3100
    labels:
      datasource: source_syslog
    out_of_order_action: rewrite_timestamp
    encoding:
      codec: json
vector_service_enabled: true
vector_service_status: started
vector_manage_service: true
vector_service_state: started
```

## Example Playbook

```yaml
- name: Apply vector
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degit.monitoring.vector
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
