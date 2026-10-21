# Ansible Collection `degit.monitoring`

[![CI](https://github.com/degitag/ansible-collection-monitoring/actions/workflows/ci.yml/badge.svg)](https://github.com/degitag/ansible-collection-monitoring/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/degitag/ansible-collection-monitoring)](https://github.com/degitag/ansible-collection-monitoring/releases)
[![Tag](https://img.shields.io/github/v/tag/degitag/ansible-collection-monitoring)](https://github.com/degitag/ansible-collection-monitoring/tags)

Dieser Branch bereitet den neuen Collection-Vertrag 2.0.0 vor. Er enthält native
Monitoringdienste, Agenten und Exporter. Es wurde noch kein Produktionsrelease
veröffentlicht. Produktionsserver wurden durch diese Überarbeitung nicht umgestellt.

## Zuständigkeit

Alloy und node_exporter werden ausschließlich hier gepflegt und entfallen aus
`degit.infrastructure`. Firewall und Host-Netzwerk bleiben bei der Host-Collection.
Optionale Firewall-Verwaltung benötigt deren separat installierte `firewall`-Rolle;
die Host-Collection hängt nicht von Monitoring ab.

Grafana Agent und Promtail sind entfernt. Bestehende Systeme wurden bereits
umgestellt; es gibt keine Migrations- oder Deinstallationsautomation.

## Plattformvertrag

- Debian 13
- Ubuntu 22.04, 24.04 und 26.04
- Rocky Linux 9 und RHEL 9
- Windows ausschließlich für den getrennten Alloy-Agentpfad

Die native Basisabnahme auf fünf eigenen Linux-VMs und einer frischen Windows-11-VM
ist in [docs/validation/README.md](docs/validation/README.md) dokumentiert. Sie prüft
acht Linux-Rollen und Windows-Alloy. Weitere Exporter, Windows Server, echtes RHEL,
Upgrades und Restore bleiben gesonderte Freigabeschritte. Synthetische Preflight-Tests
ergänzen diese Abnahme. RHEL benötigt passende abonnierte Repositories.

## Installation zur Entwicklung

Ansible Core 2.20/2.21 und Python 3.12 werden als Controller getestet. Das GitHub-
Zielrepository ist `degitag/ansible-collection-monitoring`. Die GitHub-Verweise in
den Metadaten bereiten den getrennten Transfer vor; bis dahin bleibt der bestehende
Git-Remote maßgeblich. Der Ansible-Namespace bleibt `degit.monitoring`.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/ansible-galaxy collection install -r requirements.yml -p .ansible/collections
.venv/bin/ansible-galaxy collection build --force
.venv/bin/python tools/check_collection_artifact.py degit-monitoring-2.0.0.tar.gz
.venv/bin/ansible-galaxy collection install degit-monitoring-2.0.0.tar.gz --no-deps --force -p .ansible/collections
```

## Verwendung

```yaml
- name: Configure monitoring agents
  hosts: linux_servers
  become: true
  gather_facts: true
  roles:
    - role: degit.monitoring.node_exporter
      vars:
        node_exporter_manage_firewall: false
```

Version 2 hat einen neuen Variablenvertrag. Vorhandene Playbooks werden anhand von
[docs/migration.md](docs/migration.md) angepasst. Kundenspezifische Ziele, Empfänger,
Secrets und Alarmgrenzen gehören in das jeweilige Infrastruktur-Inventory.

## Rollenstandard

`tasks/main.yml` ist der generierte Einstieg: erst Preflight, danach
`tasks/configuration.yml`. Die Plattformschicht lädt Familie, Distribution und
Release. Öffentliche Eingaben stehen in Defaults und typisierten Argument-Specs;
interne Plattformwerte dürfen Inventory-Eingaben nicht überschreiben.

Dienstaktionen und Handler respektieren `*_manage_service` und den gewünschten
Stoppzustand. Konfiguration wird vor Aktivierung validiert, wenn ein nativer
Validator vorhanden ist. Bereits vorhandene Datenverzeichnisse werden nicht gelöscht.

Die bisherigen Platzhalter `dovecot_exporter`, `ipmi_exporter`,
`keepalived_exporter` und `postfix_exporter` sind ausdrücklich nicht implementiert.
Ihr Preflight bricht vor Änderungen ab; sie zählen nicht als einsatzbereite Rollen.

## Entwicklung und Abnahme

```bash
.venv/bin/python tools/generate_role_scaffold.py
.venv/bin/python tools/format_yaml.py
.venv/bin/python tools/generate_role_scaffold.py --check
.venv/bin/pytest -q tests/unit
.venv/bin/yamllint .
PATH="$PWD/.venv/bin:$PATH" bash tests/run_role_syntax_checks.sh
PATH="$PWD/.venv/bin:$PATH" python tests/run_preflight_checks.py
PATH="$PWD/.venv/bin:$PATH" ansible-lint --offline
PATH="$PWD/.venv/bin:$PATH" bash tests/run_collection_sanity.sh degit-monitoring-2.0.0.tar.gz monitoring
```

Syntax- und Preflight-Tests müssen gegen das vorher gebaute und installierte
Artefakt laufen. CI prüft beide Controller-Versionen, das Paket, Unit-Tests,
synthetische Plattformfälle und Lint. Ein grüner Lauf ersetzt keine Laufzeitabnahme
für Backends, Windows, SELinux, Upgrades oder Datenwiederherstellung.

## Neutrales LPM-Standardprofil

Prometheus und Alertmanager aktivieren das wiederverwendbare Hostprofil in Version 2
standardmäßig. Es umfasst 34 Recording Rules, 29 Alarme und neutrale HTML-/Textmails.
Node Exporter, eigenständiger Windows Exporter und Alloy verwenden denselben Vertrag;
Kundenbranding, Empfänger, SMTP und Unternehmensziele bleiben im Infrastruktur-Repo.

- [Prometheus: LPM, Metriken und Ressourcenklassen](roles/prometheus/README.md)
- [Alertmanager: Standardmails und Unterdrückung](roles/alertmanager/README.md)
- [Validierung und Testgrenzen](docs/validation/lpm.md)
- [Neutrale Windows-Mailvorschau](docs/validation/lpm-mail-windows.html)

Die frühere LPM-Basis aus einem Kunden-Inventory darf beim Wechsel nicht zusätzlich
zur gebündelten Basis geladen werden. Kundeneigene Regeln und Vorlagen bleiben separat.

### Native Proxmox metrics

PVE 9 can send native OTLP/HTTP metrics directly to a central Alloy receiver.
Enable the optional Proxmox features in Alloy, Prometheus, Alertmanager and Grafana.
Sender configuration belongs to `lenmail.proxmox.metric_server`; customer endpoints,
credentials, cluster identities and expected nodes belong to the infrastructure
inventory. A standalone OpenTelemetry agent is not required for the native export.

## Gemeinsame Nutzung der Collections

[Gemeinsamer Nutzungsvertrag](docs/collection-usage.md) beschreibt Installation, Rollenaufbau, Abhängigkeiten und den einheitlichen lokalen Prüfaufruf `bash tests/run_checks.sh`.
