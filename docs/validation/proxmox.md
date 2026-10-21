# Native Proxmox profile acceptance — 2026-10-18

The profile is implemented across `degit.monitoring`, `lenmail.proxmox` and the
LenMail infrastructure playbook `playbooks/pve_metrics.yml`. Customer endpoints,
credentials and cluster identity remain in the infrastructure repository.

PVE 9.2.18 sent real node, storage and VM metrics through an isolated Debian 13
receiver first, then through authenticated HTTPS to the existing Alloy 1.18.0 on
observ01. The production path remains fresh after removing both test tunnels.
Unauthenticated POSTs receive 401. The existing Tempo and Loki paths remain intact.
No additional PVE agent, service restart or guest modification was needed for the
sender. Receiver configuration files were backed up before the scoped adoption.

Seven production alarms and one expected-node recording rule are healthy. The
optional required-guest alarm is tested but no production VM was arbitrarily
classified as required. CPU spikes, reclaimable cache, zero storage capacity,
source disappearance, escalation and cross-tenant matching have semantic tests.
Native Alertmanager tests validate the inhibition boundaries on an isolated
blackhole route; no test message was sent to real recipients.

Grafana Labs dashboard 23855 revision 1 (spagno) was adapted, source-attributed,
loaded into Grafana with 33 panels and all 48 PromQL targets executed successfully.
The source identity filters, guest table joins, IO-wait, disk/network rates and
freshness/alert views were corrected. Empty LXC/active-alert panels are expected
for this installation. Visual browser acceptance remains unverified because the
browser requires Grafana/Authentik sign-in; this is distinct from the verified
provisioning and query results.

Final packaged replay: observ01 `ok=24 changed=0 failed=0`; PVE
`ok=3 changed=0 failed=0`. VM 3390, seed, image and tunnels were removed. All 14
existing guests retained their names, states and nodes. Configuration suspension
and rollback use the named metric-server entry and owned rule/provider/dashboard
files; do not remove unrelated exporters or change guest runtime state.

See `proxmox-results.json` for timestamped runtime evidence, test counts, artifact
hashes and the remaining release boundaries. This acceptance is an extension to
the earlier foundation and LPM evidence, not a claim of a complete v2 production
release or native multi-node cluster acceptance.
