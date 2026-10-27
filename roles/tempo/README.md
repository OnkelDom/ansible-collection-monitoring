# tempo

Install and configure a native Grafana Tempo service.

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
tempo_version: 3.0.0
tempo_archive_sha256:
  x86_64: f4150470a5f6bf57e94dac5392c552b488932ea9e88a6ee2a75d7b969b7cb6a4
  aarch64: ca4cd9db4b39f60b9b2f2f0d06c9cfd89e52b1512431cf1e262f91f8cdccafb9
tempo_data_dir: /var/lib/tempo
tempo_http_listen_address: 127.0.0.1
tempo_otlp_listen_address: 127.0.0.1
tempo_service_enabled: true
tempo_service_state: started
tempo_config:
  target: all
  server:
    http_listen_address: '{{ tempo_http_listen_address }}'
    http_listen_port: 3200
  distributor:
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: '{{ tempo_otlp_listen_address }}:4317'
          http:
            endpoint: '{{ tempo_otlp_listen_address }}:4318'
  storage:
    trace:
      backend: local
      local:
        path: '{{ tempo_data_dir }}/traces'
      wal:
        path: '{{ tempo_data_dir }}/wal'
  usage_report:
    reporting_enabled: false
tempo_manage_service: true
```

## Example Playbook

```yaml
- name: Apply tempo
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.monitoring.tempo
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

## Native Tempo operation

Installiert Grafana Tempo als nativen systemd-Dienst aus einem per SHA256
verifizierten offiziellen Release-Archiv. Unterstuetzt Debian 12/13,
Ubuntu 22.04/24.04 und RHEL-kompatible Systeme der Version 9 auf x86_64/aarch64.
Die Rolle erfordert gesammelte Facts und `become: true`.

`tempo_config` ist die vollstaendige Konfiguration. Standardmaessig laufen die
HTTP- und OTLP-Endpunkte nur auf Loopback; fuer zentralen Empfang muss
`tempo_otlp_listen_address` explizit auf eine interne Adresse gesetzt werden.
Tempo bietet keine eigene Anmeldung. Oeffentliche Freigaben muessen daher
ausserhalb der Rolle abgesichert werden.

```yaml
- hosts: monitoring
  become: true
  roles:
    - role: degitag.monitoring.tempo
  vars:
    tempo_data_dir: /srv/monitoring/tempo
    tempo_otlp_listen_address: 10.30.30.24
```

Die Rolle validiert neue Konfiguration vor einem Dienstneustart mit
`tempo -config.verify`. Ein produktiver Trace-Restore ist separat zu pruefen.
