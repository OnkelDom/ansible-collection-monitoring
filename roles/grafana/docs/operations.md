
## Native Proxmox dashboard

Set `grafana_proxmox_dashboard_enabled: true` to provision **Proxmox | Native OTLP**
with UID `monitoring-proxmox-native` in the Infrastructure folder. It uses a
separate provider and `monitoring-proxmox` directory below `grafana_data_dir`.
Other dashboard files are untouched. A new/removed provider restarts Grafana when
service management is enabled; JSON updates are picked up every ten seconds.

The 33-panel dashboard adapts Grafana Labs dashboard 23855 revision 1 by spagno.
Source, revision and original SHA256 are recorded beside the asset. It retains the
node/VM/LXC/storage layout and adds tenant/environment/site/cluster/node filters,
metric freshness, missing sources and active cluster alerts. Disk/network rates,
IO-wait and multi-cluster guest table identity are corrected. LXC panels are
expected to be empty when no containers run; an empty active-alert table is healthy.
Select a Prometheus datasource; no external Grafana plugin is required. The
profile needs native PVE metrics processed by the supplied Alloy configuration.


## Qualifizierte Paketversion

Der Release-Standard verwendet Grafana 13.2.4. `latest` bleibt eine ausdrückliche
Betreiberentscheidung und gehört nicht zum festen Qualifikationsumfang.

## Provisionierungsgrenzen

Der allgemeine Dashboardimport übernimmt keine `*.provenance.json`-Metadaten. Das
native PVE-Dashboard gehört ausschließlich zum eigenen opt-in Provider; alte
Kopien im generischen Provisionierungsverzeichnis werden bereinigt. Dateien
werden direkt mit ihrem endgültigen Eigentümer und Modus angelegt, damit
identische Rollenläufe keine Dateirechte hin- und herwechseln.

Debian-Pakete starten Grafana während der Installation nicht automatisch; die
Konfiguration wird vor dem ersten verwalteten Start geschrieben. Administratorname
und Passwort in `grafana_security` sind Bootstrap-Eingaben für eine neue Datenbank.
Eine bestehende Grafana-Datenbank behält ihre Benutzer und Passwörter; deren
Rotation benötigt eine ausdrückliche administrative Änderung.
