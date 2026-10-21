# victoriametrics

Install and configure VictoriaMetrics.

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
victoriametrics_version: 1.57.1
victoriametrics_web_listen_address: 0.0.0.0
victoriametrics_web_listen_port: 8428
victoriametrics_binary_install_dir: /usr/local/bin
victoriametrics_system_user: "{{ victoriametrics_user | default('prometheus') }}"
victoriametrics_system_group: "{{ victoriametrics_group | default('prometheus') }}"
victoriametrics_data_dir: /var/lib/victoriametrics
victoriametrics_config_dir: /etc/victoriametrics
victoriametrics_log_level: warn
victoriametrics_log_format: json
victoriametrics_prometheus_config: {}
victoriametrics_limit_nofile: 16384
victoriametrics_config:
  storageDataPath: '{{ victoriametrics_data_dir }}'
victoriametrics_manage_service: true
victoriametrics_service_enabled: true
victoriametrics_service_state: started
```

## Example Playbook

```yaml
- name: Apply victoriametrics
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degit.monitoring.victoriametrics
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
