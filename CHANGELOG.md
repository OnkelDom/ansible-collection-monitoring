# Changelog

## Unreleased

- Align the package namespace with `lenmail.monitoring` and add the native Tempo role.
- Compile Windows/Linux alert annotation variants with a neutral fallback.
- Support configurable Prometheus/Alertmanager data paths and extra Loki configuration.
- Correct Alertmanager YAML rendering, optional Alloy values and supplied exporter checksums.
- Preserve role operating instructions during scaffold regeneration and validate the updated roles.

## 0.1.0

- Initial collection scaffold for `lenmail.monitoring`
- Imported existing monitoring roles into `roles/`
- Added generated role metadata, argument specs, and syntax test playbooks
