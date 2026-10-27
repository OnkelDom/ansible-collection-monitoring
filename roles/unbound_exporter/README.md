# unbound_exporter

Install and configure the Prometheus unbound_exporter.

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
unbound_exporter_log_level: warn
unbound_exporter_config_flags_extra:
  unbound.uri: '{{ _unbound_exporter_platform_control_uri | default("tcp://127.0.0.1:8953") }}'
unbound_exporter_manage_service: true
unbound_exporter_service_enabled: true
unbound_exporter_service_state: started
```

## Example Playbook

```yaml
- name: Apply unbound_exporter
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.monitoring.unbound_exporter
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

## Binary provenance

Bundled binaries support Linux x86_64 and aarch64. The role rejects other
architectures before installation. `files/exporter.provenance.json` records the
immutable upstream revision, source checksum, Go toolchain, dependency lock hashes
and binary hashes. Rebuild and verify with `tools/build_exporters.py`; unknown
bundled ELF files are rejected during artifact validation.


## Unbound-Steuerpfad und optionale Blockliste

Die Plattformschicht wählt den Paketstandard für den lokalen Unix-Control-Socket:
Debian/Ubuntu `/run/unbound.ctl`, Rocky/RHEL `/run/unbound/control`. Abweichende
Installationen überschreiben `unbound_exporter_config_flags_extra['unbound.uri']`.
Auf Ubuntu 22.04 muss der Betreiber Control explizit aktivieren; die Exporter-Rolle
konfiguriert den DNS-Dienst nicht selbst.
TCP-Control benötigt entsprechend konfigurierte Zertifikate und Serverfreigaben.

Blocklisten-Metriken sind optional; ein Dateipfad wird ausdrücklich über
`unbound_exporter_config_flags_extra['block-file']` angegeben. Der geprüfte
Source-Patch zählt eindeutige Domains aus `local-zone`/`local-data`, unterstützt
Dateien ohne Header oder abschließenden Zeilenumbruch und liefert keine negativen
Anzahlen. Die Herkunftsdatei verweist auf Patch und Go-Regressionstest.
