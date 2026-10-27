# squid_exporter

Install and configure the Prometheus squid_exporter.

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
squid_exporter_version: 1.8.2
squid_exporter_web_listen_address: 0.0.0.0
squid_exporter_web_listen_port: 9301
squid_exporter_binary_local_dir: /usr/local/bin
squid_exporter_system_user: prometheus
squid_exporter_system_group: prometheus
squid_exporter_log_level: info
squid_exporter_manage_service: true
squid_exporter_service_enabled: true
squid_exporter_service_state: started
```

## Example Playbook

```yaml
- name: Apply squid_exporter
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.monitoring.squid_exporter
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


`squid_exporter_version` ist für das gebündelte, überprüfte Artefakt auf 1.8.2
begrenzt. Andere Quellen erfordern einen bewussten Neubau mit neuer Provenienz;
eine abweichende Versionsnummer wird nicht stillschweigend ignoriert.

Der gebündelte Patch verwendet `/squid-internal-mgr/counters`, damit auch Squid 7
auf Ubuntu 26.04 ausgelesen wird. Ein echter HTTP-Fixturetest prüft den Pfad und
das Parsen; die native Matrix prüft `squid_up=1` gegen lokale Squid-Backends.
