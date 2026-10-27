# process_exporter

Install and configure the Prometheus process_exporter.

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
process_exporter_binary_install_dir: /usr/local/bin
process_exporter_version: 0.7.5
process_exporter_web_listen_address: 0.0.0.0
process_exporter_web_listen_port: 9256
process_exporter_config_dir: /etc/process_exporter
process_exporter_system_user: process_exporter
process_exporter_system_group: process_exporter
process_exporter_create_consul_agent_service: false
process_exporter_names: "{% raw %}\n  - name: \"{{.Comm}}\"\n    cmdline:\n      - '.+'\n{% endraw %}\n"
process_exporter_manage_service: true
process_exporter_service_enabled: true
process_exporter_service_state: started
```

## Example Playbook

```yaml
- name: Apply process_exporter
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.monitoring.process_exporter
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

## Versionsvertrag

Archive werden auf dem Ziel gegen die veröffentlichte Prüfsumme geprüft. Die native
Release-Abnahme umfasst den Wechsel 0.7.5 → 0.8.1 → 0.7.5. Version 0.8.0 wird vor
Änderungen abgewiesen: deren Upstream-Implementierung übergibt keine Listen-Adresse
an das Exporter-Toolkit und startet deshalb keinen HTTP-Listener. Die Korrektur
steht in [Upstream 0.8.1](https://github.com/ncabatoff/process-exporter/blob/v0.8.1/cmd/process-exporter/main.go).
Andere Versionen benötigen eine eigene Laufzeitprüfung.
