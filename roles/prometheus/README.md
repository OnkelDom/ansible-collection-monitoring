# prometheus

Install and configure the Prometheus server and rule files.

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
prometheus_version: 2.48.0
prometheus_data_dir: /var/lib/prometheus
prometheus_web_external_url: http://localhost:9090
prometheus_webconfig: {}
prometheus_log_level: warn
prometheus_storage_retention_time: 30d
prometheus_config_flags_extra: {}
prometheus_config:
  global:
    scrape_interval: 60s
    scrape_timeout: 10s
  rule_files:
  - /etc/prometheus/rules/*.rules
prometheus_static_targets_files: []
prometheus_alert_rules_files: []
prometheus_alert_rules_src_dir: prometheus/rules
prometheus_static_targets_src_dir: prometheus/file_sd
prometheus_platform_annotation_overrides: []
prometheus_manage_service: true
prometheus_service_enabled: true
prometheus_service_state: started
prometheus_remote_write_receiver_enabled: false
prometheus_lpm_enabled: true
prometheus_lpm_default_criticality: mid
prometheus_lpm_dashboard_url: ''
prometheus_lpm_runbook_url: ''
prometheus_proxmox_enabled: false
prometheus_proxmox_expected_nodes: []
prometheus_proxmox_expected_guests: []
prometheus_proxmox_dashboard_url: ''
```

## Example Playbook

```yaml
- name: Apply prometheus
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degitag.monitoring.prometheus
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

## Standardprofil LPM

`prometheus_lpm_enabled: true` installiert das neutrale Hostprofil automatisch in
`/etc/prometheus/lpm/host.rules` und ergänzt dessen eigene Rule-Dateiliste. Es enthält
42 Recording Rules und 53 Alarme für CPU-/Speicherdruck, Speicherreserve, OOM,
Dateisysteme/Inodes, Datenträger-I/O, Netzwerkfehler, Conntrack und Scrape-Ausfälle.
Die optionalen kernelabhängigen Signale benötigen die jeweiligen Exporter-Collector.
Anwendungsdienste, Port-/HTTP-Ziele und Business-Regeln werden im Inventory ergänzt.

Die Metrikfamilien `node_*`, `windows_*` und Telegraf-Prometheus-v2-Metriken funktionieren unabhängig vom Jobnamen,
sowohl bei direkt gescrapten Exportern als auch bei Alloy Remote Write. Windows-
Bootzeitnamen aus aktuellen und älteren Exporter-Releases werden normalisiert.
Windows Exporter benötigt `cpu`, `logical_disk`, `memory`, `net`, `os`, `system`.
Der Windows-Alloy-Pfad aktiviert diese benötigten Collector standardmäßig.
Diese Collection liefert keine separate Windows-Exporter-Installationsrolle.

Fehlende Ressourcenlabels `lpm_*_criticality` erhalten auf den Recording Rules
`prometheus_lpm_default_criticality: mid`. Vorhandene Werte `high`, `mid`, `low`
bleiben erhalten; Ressourcenklassen lassen sich über Scrape-Labels oder Alloy-
External-Labels vorgeben. Der Standard ist keine automatische Erkennung von
Geschäftskritikalität. I/O-Alarme des übernommenen Profils gelten für Klasse `high`.

Für direkte Scrapes ist `monitoring_profile: lpm` als Target-Label zu setzen, damit
auch `up == 0` erkannt wird. Ressourcenregeln erkennen die Metrikfamilien auch ohne
dieses Label. Alloy setzt das Profil im Pipelinepfad über `alloy_lpm_enabled: true`.
Ein vollständig ausgefallener Remote-Write-Sender kann kein `up=0` mehr senden;
externes Heartbeat-/Erreichbarkeitsmonitoring bleibt dafür erforderlich.

`tenant`, `environment`, `site` bleiben in Aggregationen und Verknüpfungen erhalten.
`instance` muss innerhalb dieser Grenzen einen Host eindeutig identifizieren.
Für denselben Host wird genau eine maßgebliche Metrikquelle konfiguriert; paralleles
Scrapen von Node Exporter und Alloy erzeugt sonst eigenständige Alarmserien.

Kundenbranding, Empfänger, Unternehmensdomains und feste Host-/Laufwerksausnahmen
sind nicht enthalten. Optionale Links kommen aus `prometheus_lpm_dashboard_url`
und `prometheus_lpm_runbook_url`; spezifische Texte aus
`prometheus_platform_annotation_overrides`. Windows-/Linux-Kommandos richten sich
nach der überwachten Plattform und nicht nach dem Prometheus-Server.

Bei Übernahme aus einem bestehenden Inventory sind die bisherigen LPM-Basisregeln
aus dessen Dateiliste zu entfernen, damit Regeln nicht doppelt geladen werden.
Dessen Kunden-/Anwendungsregeln bleiben separat. `prometheus_lpm_enabled: false`
entfernt ausschließlich die von der Collection verwaltete LPM-Datei und deren
impliziten Config-Eintrag. Explizite eigene `rule_files` bleiben erhalten.

## Native Proxmox profile

Enable `prometheus_proxmox_enabled` and explicitly populate
`prometheus_proxmox_expected_nodes` with tenant, environment, site, cluster and
node. Run `degitag.proxmox.metric_server` once per PVE cluster. Every member sends
its own statistics; a cluster-shared pmxcfs entry must not be reconciled
concurrently from every member. Independent clusters need distinct identities.
The owned rule file is `/etc/prometheus/proxmox/native.rules`; disabling the
profile removes only that file and its automatically added rule path.

Seven alarms cover missing metric sources and sustained CPU, memory and storage
pressure. Missing means no sample younger than 180 seconds for a further 5
minutes, not proof that the hypervisor or guests have crashed. CPU warns above
90% for 15 minutes and is critical above 98% for 10 minutes. Memory uses total
minus available memory, so reclaimable cache is not automatically pressure;
thresholds are 90%/15m and 97%/10m. Storage excludes zero-capacity values and uses
85%/15m and 95%/10m. Severity is WARN/ERROR. Enable the matching Alertmanager
profile to inhibit only the same tenant, environment, site, cluster, node,
storage and alert family. Alertmanager grouping/recipients remain inventory policy.

Optionally list `prometheus_proxmox_expected_guests` with tenant, environment,
site, cluster and VMID. Only these guests alert after ten minutes without positive
uptime. Expected-node outages suppress guest cascades; migrate guests within the
same cluster without changing their expectation. Empty list is the safe default:
stopped test VMs are not failures. An entirely lost monitoring stack needs an
external heartbeat; this profile cannot report its own total loss.

Use `prometheus_proxmox_dashboard_url` for the dashboard link in notifications.
PVE guest memory/virtual disk statistics are not a replacement for in-guest
Linux/Windows LPM (filesystem capacity, services and application health).
Validation: `PROMTOOL=/path/to/promtool python tests/run_proxmox_checks.py`.

## Current filesystem presence

Linux capacity and inode recordings require a corresponding current raw metric.
A removed or deliberately excluded bind alias therefore disappears from recording
rules even while its old samples remain inside the 15-minute averaging window.
Namespace labels participate in the join; another tenant cannot keep an expired
mount alive. Inode monitoring uses its own current inode metric independently of
byte capacity. Windows volume rules are unchanged. Bind aliases must still be
excluded explicitly at the collector; independent submounts remain monitored.


## Gemeinsame LPM-Matrix

Die maschinenlesbare Quellen-, Einheiten- und Schwellenwertmatrix liegt in
`files/lpm/source-matrix.yml`. Alloy unter Linux und Node Exporter verwenden die
`node_*`-Familie; Alloy unter Windows verwendet die `windows_*`-Familie. Telegraf
unter Linux benötigt Prometheus-Ausgabe `metric_version = 2` und die Eingänge
`cpu`, `system`, `mem`, `swap`, `disk`, `diskio`, `net`, `kernel_vmstat`.
`cpu` muss `totalcpu = true` liefern. Installation und Telegraf-Konfigurations-API
bleiben in `degitag.infrastructure.telegraf`.

| Signal | Alloy / Node Exporter | Telegraf | Normalisierte Einheit |
| --- | --- | --- | --- |
| CPU | CPU-Zeit als Counter | `cpu_usage_idle{cpu="cpu-total"}` | Prozent beschäftigt, 15-Minuten-Mittel |
| RAM | verfügbar / gesamt | `mem_available / mem_total` | Prozent belegt ohne verfügbare Cache-Reserve |
| Swap | frei / gesamt, vmstat | `swap_free / swap_total`, `kernel_vmstat_pswp*` | Prozent und Seiten/s |
| Dateisystem / Inodes | Filesystem-Collector | `disk_used_percent`, `disk_total`, Inode-Zähler | Prozent, nur aktuell vorhandene Kapazität |
| I/O | Sekunden-Counter | Millisekunden-Counter aus `diskio` | Auslastung 0–1, Latenz ms, Warteschlange |
| Netzwerk | netdev-Counter | `net_*` | Byte/s und Fehler bzw. Drops/s |
| Conntrack | optionaler Conntrack-Collector | optionales `conntrack` | Auslastung 0–1 |
| Dienste | optionaler systemd-/Windows-Service-Collector | optionales `systemd_units` | 0 ist bereit; nur explizit erwartete Dienste |
| Port / HTTP | Blackbox Exporter oder explizite Alloy-Blackbox-Komponente | `net_response`, `http_response` | 0 ist erfolgreich; nur explizit markierte Ziele |

Die Klassenschwellen sind für alle Quellen gleich. Verglichen wird jeweils strikt
`>`; zusätzliche Druck-/OOM-/Reserve-Alarme bleiben ergänzend aktiv.

| Klasse | CPU WARN / ERROR | RAM WARN / ERROR | Dateisystem WARN / ERROR | Haltezeit |
| --- | --- | --- | --- | --- |
| high | 30 / 40 % | 60 / 75 % | 70 / 85 % | 15 Minuten |
| mid | 70 / 85 % | 80 / 90 % | 80 / 90 % | 15 Minuten |
| low | 85 / 95 % | 90 / 95 % | 90 / 95 % | 60 Minuten |

CPU und I/O ignorieren die ersten zehn Minuten nach dem Boot. Für I/O `high`
gelten Auslastung 0,60 / 0,80 und Latenz 10 / 25 ms, jeweils 15 Minuten;
Warteschlange über 5 alarmiert nach 15 Minuten. Conntrack verwendet
high 0,50 / 0,70, mid 0,70 / 0,85 (5 Minuten), low 0,85 / 0,95 (10 Minuten).
Dienst-, Port- und HTTP-Prüfungen alarmieren bei Fehlercode ungleich 0 nach
30 Sekunden / 1 Minute / 2 Minuten für high / mid / low.

Dienste benötigen ausdrücklich `lpm_service_expected="true"` und einen aktivierten
Collector. Ein fehlender Dienst-Messwert ist kein Nachweis eines laufenden Dienstes;
für das vollständige Verschwinden ist eine externe Erwartungsliste erforderlich.
Port-/HTTP-Metriken benötigen `monitoring_profile="lpm"`; Blackbox-Probes zusätzlich
`probe_kind="port"` bzw. `"http"`. Ein vorhandenes `target` bleibt erhalten, sonst
wird es aus der Probe-Instanz abgeleitet. Node Exporter führt selbst keine Probes aus.
Die benötigten Ziele und erwarteten Dienste bleiben im Betreiber-Inventory.

Identität ist `instance` innerhalb `tenant`, `environment`, `site`; Ressourcen
behalten `path`, `device`, `name`, `interface` und das konkrete Probe-Ziel. Eine
maßgebliche Quelle je Host bleibt der Betriebsvertrag. Werden versehentlich
Node- und Telegraf-Familien mit derselben Identität angeboten, bevorzugt die
Normalisierung Node pro Ressource und mittelt die unterschiedlichen Quellen nicht.
Alloy und ein separater Node Exporter sind anhand der gleichen Metrikfamilie nicht
automatisch unterscheidbar. Null-Kapazitäten erzeugen keine Kapazitätsreihe;
entfernte Telegraf-Mounts laufen ebenso aus wie entfernte Node-Mounts.

PSI-Drucksignale stehen in der Telegraf-Basis nicht zur Verfügung. Sie werden nicht
aus Load Average oder Cache-Belegung erfunden. Windows-Commitdruck benötigt den
Windows-Memory-Collector; OOM benötigt einen tatsächlichen Kernel-vmstat-Counter.
Der OOM-Alarm bleibt nach seinem Ereignisfenster noch 15 Minuten aktiv. Ein komplett
verstummter Remote-Write-Sender benötigt ein unabhängiges Heartbeat-Monitoring.

Die Einheiten folgen den Upstream-Verträgen für
[Telegraf diskio](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/diskio),
[kernel_vmstat](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/kernel_vmstat)
und [conntrack](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/conntrack).
Semantische Tests prüfen alle Quellen, Klassen, Haltezeiten, Counter-Resets,
Null-Kapazitäten, Cache-Reserve, aktuelle Mount-Präsenz und Mandantengrenzen.
