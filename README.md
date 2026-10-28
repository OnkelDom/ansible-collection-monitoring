# Ansible Collection `degitag.monitoring`

[![CI](https://github.com/degitag/ansible-collection-monitoring/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/degitag/ansible-collection-monitoring/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/degitag/ansible-collection-monitoring)](https://github.com/degitag/ansible-collection-monitoring/releases)
[![Tag](https://img.shields.io/github/v/tag/degitag/ansible-collection-monitoring?sort=date)](https://github.com/degitag/ansible-collection-monitoring/tags)
![Ansible Core](https://img.shields.io/badge/ansible--core-2.20%20%7C%202.21-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Native Monitoringdienste, Agenten, Exporter sowie neutrale Host- und Proxmox-Alarmprofile. Version 2.0.0 vereinheitlicht den Repository-Vertrag und den Namespace `degitag`. Ein Release führt keinen Produktionsrollout aus.

## Verantwortung und Architektur

Alloy und Node Exporter werden ausschließlich hier gepflegt. Firewall und Host-Netzwerk gehören zu `degitag.infrastructure`; deren optionale Firewall-Rolle wird additiv eingebunden. Monitoring ist keine Abhängigkeit der Host-Baseline. Die Telegraf-Installation bleibt bei Infrastructure, während der gemeinsame LPM-Metrik-/Alarmvertrag hier liegt.

Grafana Agent und Promtail sind entfernt. Es gibt keine automatische Migration oder Deinstallation. Rollen verwenden generierte Einstiege mit Preflight, typisierte öffentliche Eingaben, geschichtete Plattformvariablen und Dienstschalter, die auch für Handler gelten. Konfiguration wird vor Aktivierung mit nativen Validatoren geprüft, soweit verfügbar.

### LPM und native Proxmox-Metriken

Das neutrale LPM-Profil normalisiert Alloy-/Node-Exporter- und Telegraf-Metriken in 42 Recording Rules und 53 Alarme. Die Klassen high/mid/low steuern CPU-, Speicher-, Dateisystem-, Conntrack-, Dienst- und Probe-Schwellen. 135 semantische Regelszenarien sowie 25 echte Alertmanager-Inhibitionstests prüfen Quellen, Einheiten, Laufzeiten und Ressourcengrenzen. Quelle, Ressourcenklassen und verfügbare Collector stehen in der [Prometheus-Rollenbeschreibung](roles/prometheus/README.md). Kundenbranding, SMTP, Empfänger, Ziele und anwendungsspezifische Regeln gehören in das Betreiber-Inventory. [Alertmanager](roles/alertmanager/README.md) enthält die passende, nach Ressource und Mandant begrenzte Inhibition.

PVE 9 kann native OTLP/HTTP-Metriken an Alloy senden. Die optionalen Profile in Alloy, Prometheus, Alertmanager und Grafana ergänzen dies um Regeln und Dashboard. Senderkonfiguration gehört zu `degitag.proxmox.metric_server`; Endpunkte, Credentials und erwartete Knoten/Gäste gehören ins Inventory. Ein zusätzlicher PVE-Agent ist nicht erforderlich.

## Plattformen und Laufzeit

Linux-Zielmatrix: Debian 13, Ubuntu 22.04/24.04/26.04 und Rocky/RHEL 9. Die native Abnahme der RedHat-Familie erfolgt auf ausdrücklichen Nutzerwunsch mit Rocky 9; ein abonniertes RHEL-System wurde nicht separat geprüft. Windows besitzt einen eigenen Alloy-Pfad und eigene Tests.

Controller-Basis: Python 3.12 und Ansible Core 2.20/2.21. Die aktuelle [Release-Abnahme](docs/validation/release-readiness-2026-10-27.md) ergänzt die historische Abnahme um alle 21 Linux-Rollen, Windows Server 2025 und die quellenübergreifende LPM-Matrix. Die [historische native Abnahme](docs/validation/README.md) dokumentiert acht Kernrollen auf fünf Linux-Plattformen und Alloy auf Windows 11. Weitere datierte Nachweise stehen in `docs/validation/`. Historische Namespaces und Artefaktprüfsummen werden nicht nachträglich umetikettiert. Eine Controllerprüfung ersetzt keine Laufzeit-, Upgrade- oder Restore-Abnahme.

## Installation

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
make prepare
make build
.venv/bin/python tools/check_collection_artifact.py degitag-monitoring-2.0.0.tar.gz
.venv/bin/python tools/check_monitoring_artifact.py degitag-monitoring-2.0.0.tar.gz
.venv/bin/ansible-galaxy collection install degitag-monitoring-2.0.0.tar.gz --no-deps --force -p .ansible/collections
```

Unter Linux wird Python 3.12 aus der lokalen Controller-Installation verwendet. Optionales Firewall-Management benötigt zusätzlich die separat gebaute/installierte `degitag.infrastructure`-Collection. Der tatsächliche Git-Remote bleibt maßgeblich; eine Namespace-Änderung transferiert kein GitHub-Repository.

## Verwendung

```yaml
- name: Configure monitoring agents
  hosts: linux_servers
  become: true
  gather_facts: true
  roles:
    - role: degitag.monitoring.node_exporter
      vars:
        node_exporter_manage_firewall: false
```

Für einen Host wird eine maßgebliche Metrikquelle festgelegt. Mandant, Umgebung, Standort und Ressourcenklassen werden im Inventory definiert. Secrets stammen aus Vault oder einem Secret Store.

## Rollen

| Bereich | Rollen |
| --- | --- |
| Agenten und Pipeline | `alloy`, `node_exporter`, `vector` |
| Metriken, Logs, Traces und Darstellung | `prometheus`, `alertmanager`, `loki`, `tempo`, `grafana`, `victoriametrics`, `pushgateway` |
| Exporter | `blackbox_exporter`, `consul_exporter`, `ilo5_exporter`, `postgresql_exporter`, `process_exporter`, `redis_exporter`, `snmp_exporter`, `squid_exporter`, `systemd_exporter`, `unbound_exporter`, `unifi_poller` |

Die 21 Rollen besitzen eigene READMEs, Metadaten, Argument-Specs und Tests. Die nie implementierten Platzhalter für Dovecot, IPMI, Keepalived und Postfix werden nicht ausgeliefert.

### Gebündelte Exporter

iLO5, Squid und Unbound werden für Linux AMD64 und ARM64 aus festgelegten Upstream-Commits und gesperrten Go-Modulabhängigkeiten gebaut. `roles/*/files/exporter.provenance.json` dokumentiert Quellen, Toolchain, Anpassungen und Prüfsummen. Paketprüfungen verwerfen unbekannte oder veränderte ELF-Dateien.

```bash
.venv/bin/python tools/build_exporters.py --check
# Reproduzierbarer Neubau mit der festgelegten Go-Version:
.venv/bin/python tools/build_exporters.py
```

## Repository-Struktur

Der gemeinsame Vertrag aller fünf Collections steht in [docs/repository-standard.md](docs/repository-standard.md).

| Pfad | Zweck |
| --- | --- |
| `roles/`, `plugins/`, `meta/` | Ausgelieferte Rollen, Filter und Collection-Metadaten |
| `tools/` | Scaffold, Formatierung, Repository-/Artefaktprüfung und reproduzierbare Exporter-Builds |
| `tests/unit/`, `tests/integration/` | Vertrags-/Unitprüfungen und native Labortests |
| `tests/run_checks.sh` | Gemeinsamer vollständiger Prüfeinstieg |
| `docs/validation/` | Datierte Nachweise mit Artefaktbezug und Prüfgrenzen |
| `.github/` | CI, Release-Pipeline und Dependabot |

## Entwicklung und Checks

```bash
.venv/bin/python tools/generate_role_scaffold.py
.venv/bin/python tools/format_yaml.py
make test
```

Gemeinsame Ziele: `prepare`, `lint`, `syntax`, `unit`, `test`, `ci`, `build`, `package-smoke`. `make test` und `make ci` delegieren an `bash tests/run_checks.sh`; GitHub Actions verwendet dasselbe Skript. Es prüft Repository-Vertrag, Scaffold, Unit-Tests, YAML, gebaute/installierte Artefakte, Preflights, Syntax, Lint, Sanity sowie semantische LPM-/Proxmox-Regeln und Mailvorlagen. Die dafür benötigten CLI-Archive werden gegen Upstream-SHA256 geprüft und lokal gecacht.

Native Tests benötigen ausdrücklich befüllte Lab-Inventories. Destruktive Restore-Prüfungen sind auf markierte Wegwerf-Gäste begrenzt. Weitere Hinweise stehen in [CONTRIBUTING.md](CONTRIBUTING.md).

## CI und Releases

CI prüft Python 3.12 mit Core 2.20 und 2.21. Actions sind nach Commit-SHA gepinnt, Checkout-Credentials werden nicht persistiert. Ein Release erfordert einen expliziten `v<galaxy-version>`-Tag und erfolgreiche Checks; das konkret benannte und geprüfte Collection-Artefakt wird an den GitHub-Release angehängt. Es gibt keine automatische Galaxy-Publikation und kein Deployment.

Die frühere begrenzte Proxmox-Einführung ist [separat dokumentiert](docs/validation/proxmox.md). Sie ist keine pauschale Freigabe aller Version-2-Rollen.

## Migration

Version 2 verwendet einen neuen Variablen- und Namespace-Vertrag. Aufrufe heißen `degitag.monitoring.*`; alte Installationen werden nicht automatisch entfernt. Die [Migrationshinweise](docs/migration.md) behandeln Besitzgrenzen, entfernte Rollen, Inventories und bisherige LPM-Doppeldefinitionen. Der [gemeinsame Nutzungsvertrag](docs/collection-usage.md) beschreibt das Zusammenspiel mit Infrastructure, Database, K3s und Proxmox.

## Sicherheit

Siehe [SECURITY.md](SECURITY.md). Keine Secrets oder produktiven Ziele in Defaults, Beispielen, Logs oder Artefakten. Backups und Datenformate müssen zum konkreten Upgrade-/Rückbaupfad passen; eine Dienstbereitschaft allein belegt keine Datenaufnahme.

## Lizenz

Die Collection steht unter der MIT-Lizenz, siehe [LICENSE](LICENSE). Importierte Komponenten, Quelltexte und Dashboard-Anteile behalten ihre jeweiligen Lizenz- und Herkunftshinweise.
