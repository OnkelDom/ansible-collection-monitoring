# alertmanager

Install and configure Prometheus Alertmanager.

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
alertmanager_version: 0.27.0
alertmanager_data_dir: /var/lib/alertmanager
alertmanager_log_level: warn
alertmanager_webconfig: {}
alertmanager_config_dir: /etc/alertmanager
alertmanager_web_external_url: http://localhost:9093
alertmanager_template_files: []
alertmanager_template_src_dir: alertmanager
alertmanager_config_flags_extra: {}
alertmanager_cluster: {}
alertmanager_resolve_timeout: 5m
alertmanager_smtp: {}
alertmanager_time_intervals: []
alertmanager_inhibit_rules: []
alertmanager_route:
  receiver: blackhole
  group_by:
  - alertname
  repeat_interval: 4h
  group_interval: 5m
alertmanager_routes: []
alertmanager_manage_service: true
alertmanager_service_enabled: true
alertmanager_service_state: started
alertmanager_lpm_enabled: true
alertmanager_lpm_inhibit_rules:
- source_matchers:
  - monitoring_profile="lpm"
  - severity="ERROR"
  target_matchers:
  - monitoring_profile="lpm"
  - severity="WARN"
  equal:
  - instance
  - tenant
  - environment
  - site
  - category
  - path
  - interface
  - alert_family
  - platform
alertmanager_proxmox_enabled: false
alertmanager_proxmox_inhibit_rules:
- source_matchers:
  - severity="ERROR"
  - monitoring_profile="proxmox"
  target_matchers:
  - severity="WARN"
  - monitoring_profile="proxmox"
  equal:
  - tenant
  - environment
  - site
  - cluster
  - node
  - storage
  - alert_family
```

## Example Playbook

```yaml
- name: Apply alertmanager
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: degit.monitoring.alertmanager
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

## Neutrale Standardmails und Alarmunterdrückung

`alertmanager_lpm_enabled: true` installiert `monitoring-email.tmpl`. Jeder über
`alertmanager_routes[].config.email_configs` konfigurierte Mailempfänger erhält
standardmäßig HTML, Text und Betreff aus `monitoring.mail.html`,
`monitoring.mail.text`, `monitoring.mail.subject`. Explizite `html`, `text` und
`headers.Subject` bleiben unverändert. Empfänger, SMTP, Absender und Branding
werden ausschließlich vom aufrufenden Inventory vorgegeben. Ohne konfigurierte
Empfänger bleibt der sichere Blackhole-Standard aktiv.

Die neutralen Vorlagen unterscheiden aktiv/entwarnt, Priorität, Befund, Auswirkung,
Handlung und optionale Dashboard-/Runbook-Links. HTML-Inhalte werden beim Rendern
escaped. Zeitangaben verwenden UTC und hängen nicht von der Host-Zeitzone ab.
Optionales `owner` bezeichnet die Betriebszuständigkeit, keinen fest codierten
Unternehmensnamen. Unternehmensvorlagen können im Infrastruktur-Repo bleiben und
über die vorhandenen Template-/Mailkonfigurationsvariablen eingebunden werden.

Der Standard unterdrückt einen LPM-WARN nur bei einem passenden LPM-ERROR derselben
Alarmfamilie, Instanz, Plattform, Ressource und Mandanten-/Umgebungsgrenze.
`alertmanager_lpm_inhibit_rules` erlaubt eine explizite Anpassung;
`alertmanager_inhibit_rules` ergänzt andere Betriebsregeln. Das unterdrückt keine
anderen Mandanten oder Dateisysteme. Resolved-Mails richten sich weiter nach dem
jeweiligen `send_resolved` der Empfängerkonfiguration.

`alertmanager_lpm_enabled: false` entfernt die verwaltete Standardvorlage und deren
implizite Mail-/Inhibition-Defaults. Eigene Vorlagen und Routen bleiben erhalten.
Vor dem Aktivieren neuer Routen müssen mit `amtool check-config` und den
Template-Renderprüfungen die tatsächlichen Empfänger und Darstellungen geprüft
werden. Rendering ist kein Nachweis einer SMTP-/Postfachzustellung.

## Proxmox alert escalation

Set `alertmanager_proxmox_enabled: true` to add WARN suppression by ERROR only
within the same tenant/environment/site/cluster/node/storage/alert_family.
CPU, memory and different storage resources do not suppress one another.
The existing neutral notification templates display the supplied descriptions,
next steps and optional dashboard URL. SMTP, recipients and external branding
remain inventory policy; no test notification is sent by enabling this profile.
