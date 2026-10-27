# Changelog

## 2.0.0

- Rename the collection and sibling references to `degitag`; preserve historical validation evidence.
- Remove the four unimplemented exporter placeholders from the artifact.
- Rebuild bundled iLO5/Squid/Unbound exporters from pinned sources and updated locked dependencies for AMD64/ARM64; verify provenance and reproducibility.
- Install checksum-verified exporter releases on targets and honor version and service policy changes.
- Remove hidden Redis/iLO credentials and implicit Consul registration; pin and validate Vector packages/configuration.

- Move Alloy and node_exporter ownership out of default_server into monitoring.
- Remove Grafana Agent and Promtail without migration automation.
- Introduce generated preflight/platform layers, service guards and artifact-based controller validation.
- Remove customer defaults and make configuration inputs explicit.
- Adopt the shared five-collection repository, README, CI, artifact and release contract.
- Integrate the Alloy/Node Exporter/Telegraf LPM source matrix: 42 recordings, 53 alarms, resource-scoped inhibition, 135 semantic scenarios and 25 real Alertmanager tests.
- Pin Alloy, Grafana and Vector defaults; qualify native services on five Linux platforms and Alloy on Windows Server 2025. See the dated validation report for exact runtime, upgrade and restore scope; no production deployment is included.

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
