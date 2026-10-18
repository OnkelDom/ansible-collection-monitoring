# Ansible Collection: `lenmail.monitoring`

Diese Collection bundelt Monitoring-Rollen fuer Linux-Systeme und fuehrt die bereits vorhandenen Standalone-Rollen in einer gemeinsamen Collection zusammen.
Jede Rolle soll ein einheitliches Geruest mit `README.md`, `meta/main.yml`, `meta/argument_specs.yml` und `tests/test.yml` erhalten.

## Zielplattformen

Die Collection ist auf folgende Baseline ausgerichtet:

- Ubuntu 22.04+
- Debian 12+
- RHEL 9+

Nicht jede Rolle ist auf jeder Plattform bereits vollstaendig validiert. Abweichungen und Einschraenkungen sollen pro Rolle dokumentiert werden.

## Rollen

Die Collection enthaelt derzeit diese Rollen:

- `alertmanager`
- `alloy`
- `blackbox_exporter`
- `consul_exporter`
- `dovecot_exporter`
- `grafana`
- `grafana_agent`
- `ilo5_exporter`
- `ipmi_exporter`
- `keepalived_exporter`
- `node_exporter`
- `postfix_exporter`
- `postgresql_exporter`
- `process_exporter`
- `prometheus`
- `promtail`
- `pushgateway`
- `redis_exporter`
- `snmp_exporter`
- `squid_exporter`
- `systemd_exporter`
- `tempo`
- `unbound_exporter`
- `unifi_poller`
- `vector`
- `victoriametrics`

## Installation

```bash
ansible-galaxy collection install git+https://github.com/OnkelDom/ansible-collection-monitoring.git
```

Oder ueber eine `requirements.yml`:

```yaml
collections:
  - name: git+https://github.com/OnkelDom/ansible-collection-monitoring.git
```

## Verwendung

```yaml
- name: Monitoring stack
  hosts: all
  become: true
  roles:
    - role: lenmail.monitoring.node_exporter
    - role: lenmail.monitoring.prometheus
```

## Entwicklung

Lokale Hilfsmittel:

- Collection-Abhaengigkeiten: `requirements.yml`
- Test-Abhaengigkeiten: `requirements-test.txt`
- Rollen-Generator: `tools/generate_role_scaffold.py`

Generator ausfuehren:

```bash
python3 tools/generate_role_scaffold.py
```

Drift pruefen:

```bash
python3 tools/generate_role_scaffold.py --check
```

## Lizenz

MIT
