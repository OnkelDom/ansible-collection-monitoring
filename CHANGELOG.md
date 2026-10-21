# Changelog

## 2.0.0 preparation

- Move Alloy and node_exporter ownership out of default_server into monitoring.
- Remove Grafana Agent and Promtail without migration automation.
- Introduce degit namespace, generated preflight/platform layers, service guards and artifact-based controller validation.
- Remove customer defaults and make configuration inputs explicit.
- Runtime, upgrade and restore qualification is pending; this is not a released version.

## Previous main changes

- Align the package namespace with `lenmail.monitoring` and add the native Tempo role.
- Compile Windows/Linux alert annotation variants with a neutral fallback.
- Support configurable Prometheus/Alertmanager data paths and extra Loki configuration.
- Correct Alertmanager YAML rendering, optional Alloy values and supplied exporter checksums.
- Preserve role operating instructions during scaffold regeneration and validate the updated roles.

## 0.1.0

- Initial collection scaffold for `lenmail.monitoring`
- Imported existing monitoring roles into `roles/`
- Added generated role metadata, argument specs, and syntax test playbooks

- Add opt-in native PVE OTLP reception with independent source identity and remote write.
- Add expected-node/guest monitoring, sustained resource alerts and scoped severity inhibition.
- Add a neutral Proxmox dashboard adapted from Grafana Labs 23855 revision 1 (spagno).

- Support exact, escaped Linux filesystem alias exclusions in Alloy; gate capacity/inode recordings on current source metrics to expire removed bind mounts without merging independent filesystems.
