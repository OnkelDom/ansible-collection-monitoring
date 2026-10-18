## Native Tempo operation

Installiert Grafana Tempo als nativen systemd-Dienst aus einem per SHA256
verifizierten offiziellen Release-Archiv. Unterstuetzt Debian 12/13,
Ubuntu 22.04/24.04 und RHEL-kompatible Systeme der Version 9 auf x86_64/aarch64.
Die Rolle erfordert gesammelte Facts und `become: true`.

`tempo_config` ist die vollstaendige Konfiguration. Standardmaessig laufen die
HTTP- und OTLP-Endpunkte nur auf Loopback; fuer zentralen Empfang muss
`tempo_otlp_listen_address` explizit auf eine interne Adresse gesetzt werden.
Tempo bietet keine eigene Anmeldung. Oeffentliche Freigaben muessen daher
ausserhalb der Rolle abgesichert werden.

```yaml
- hosts: monitoring
  become: true
  roles:
    - role: lenmail.monitoring.tempo
  vars:
    tempo_data_dir: /srv/monitoring/tempo
    tempo_otlp_listen_address: 10.30.30.24
```

Die Rolle validiert neue Konfiguration vor einem Dienstneustart mit
`tempo -config.verify`. Ein produktiver Trace-Restore ist separat zu pruefen.
