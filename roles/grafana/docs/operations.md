
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
