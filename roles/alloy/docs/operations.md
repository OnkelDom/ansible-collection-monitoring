## Ownership

This role is owned exclusively by `degit.monitoring`. Host firewall policy remains in `degit.infrastructure`.

## Native Proxmox OTLP receiver

Set `alloy_proxmox_enabled: true` on the central Linux receiver. This feature is
independent of the local host pipeline and uses its own remote-write component.
`alloy_proxmox_remote_write_url` must point to the Prometheus write receiver.
The default listener `127.0.0.1:14318` is intended behind a TLS reverse proxy;
14318 avoids an existing Tempo listener on 4318. Route exactly `/v1/metrics`.
Use `alloy_proxmox_htpasswd_file` with a high-entropy per-environment credential.
An externally bound listener requires both TLS certificate/key and htpasswd.
Never disable PVE certificate verification. Secrets stay in private files/Vault.

`alloy_proxmox_labels` assigns trusted tenant/environment/site labels at the
receiver. All sources sharing this receiver must belong to that same trust domain.
Separate customers/environments need separate authenticated receiver instances or
components, not client-supplied tenant labels. Cluster/node identity comes from
PVE resource attributes; `monitoring.cluster` supplies the globally unique cluster
name, including on standalone PVE. Guest identity includes tenant, environment,
site, cluster and VMID; migration does not change that identity. Local receiver
host labels and the host LPM profile are never added to PVE metrics.

Metric unit suffix inference is disabled deliberately: native PVE already names
counters, and inferred units vary across field names. The supplied rules and
dashboard consume stable raw `proxmox_*` names. Existing dashboards using
`*_bytes` or `*_seconds` must be adapted and must not be mixed into this profile.

For adopting an existing Linux Alloy pipeline, `tasks_from: proxmox_receiver`
validates and adds only a marked block. The full role renders the same marked
block. Set enabled false to remove it. The scoped task preserves existing source
and log pipelines; reapply it after any older baseline that replaces config.alloy.
No extra agent is required on PVE for this native metric export. Local Alloy and
Node Exporter remain responsible for journal/crash logs and detailed OS metrics.

## Filesystem aliases and bind mounts

Use `alloy_linux_filesystem_mount_points_exclude_extra` for audited bind-mount
aliases whose capacity is already monitored at a canonical mount. The list is
empty by default and contains absolute exact mount paths. The collection escapes
regex characters and anchors each alias; an independently mounted descendant is
preserved. `/` and ambiguous trailing slashes are rejected. Never deduplicate all
mounts solely by device: Btrfs subvolumes, quotas and independent mounts can have
different capacity semantics. Keep at least one canonical mount per filesystem.
Excluding an alias removes both byte and inode duplicates while canonical LPM
capacity alerts remain unchanged. Stale historical samples expire normally.
Legacy custom Alloy blocks must explicitly consume the same variables; the
structured pipeline applies them automatically. No customer paths are defaults.
