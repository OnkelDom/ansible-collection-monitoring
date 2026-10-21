# Gemeinsamer Nutzungsvertrag

Die vier Collections verwenden denselben Controller- und Rollenstandard. Der GitHub-Owner `degitag` ist unabhängig vom Ansible-Namespace `degit`.

| Collection | Verantwortung |
| --- | --- |
| `degit.infrastructure` | Betriebssystem, Netzwerk, Firewall und allgemeine Host-Dienste |
| `degit.monitoring` | Monitoringdienste, Agenten und Exporter |
| `degit.database` | Datenbanken, Caches, Patroni und etcd |
| `degit.k3s` | K3s-Cluster und Kubernetes-Integrationen |

## Installation und Prüfungen

Im jeweiligen Checkout:

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/ansible-galaxy collection install -r requirements.yml
bash tests/run_checks.sh
```

Die Prüfungen sammeln keine produktiven Hostdaten und führen kein Deployment aus. Abhängigkeiten zwischen noch nicht veröffentlichten Collections werden vorher aus den lokalen Checkouts gebaut und installiert. `degit.infrastructure` muss vor K3s und vor aktivierter Firewall-Delegation installiert sein. Die CI verwendet hierfür einen expliziten Checkout des Host-Repositories.

## Playbooks und Rollen

Beispiele sammeln Facts mit `gather_facts: true`; Rollen ergänzen fehlende benötigte Facts am Einstieg. Auf eine unterstützte Distribution folgen Familien-, Distributions- und Release-Variablen. Öffentliche Eingaben stehen in `defaults/main.yml` und `meta/argument_specs.yml`. Rollen werden mit ihrem vollständigen Namen eingebunden.

Dienstrollen verwenden soweit fachlich möglich `<rolle>_manage_service`, `<rolle>_service_enabled` und `<rolle>_service_state`. Handler respektieren diese Steuerung. Fachliche APIs und Rollenpräfixe bleiben je Dienst unterschiedlich. Secrets stammen aus Vault bzw. einem Secret Store.

Host-Netzwerk und Portregeln gehören ausschließlich Infrastructure. Optionale Firewall-Regeln werden additiv an `degit.infrastructure.firewall` delegiert. Die gemeinsame Zielmatrix ist Debian 13, Ubuntu 22.04/24.04/26.04 und Rocky/RHEL 9; Rollen können dokumentierte engere Grenzen haben. Windows-Alloy bleibt ein getrenntes Monitoring-Ziel. RHEL benötigt abonnierte Repositories und eine eigene Abnahme.

Ein grüner lokaler Prüflauf bestätigt Verträge, Syntax, Lint und Artefakt. Dienststart, SELinux, Reboot, Replikation, Failover und Restore werden auf dedizierten Testsystemen geprüft. Der jeweilige Nachweis und offene Lücken stehen in `docs/validation/`.
