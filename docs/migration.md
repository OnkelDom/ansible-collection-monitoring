# Monitoring Collection Version 2

Ziel ist `degit.monitoring:2.0.0`. Dieser Branch bereitet einen neuen Vertrag vor;
er ist noch kein freigegebener Produktionsrelease. Repository-Transfer, Release-Tags
und produktive Upgrades werden getrennt durchgeführt.

## Verantwortung

`alloy` und `node_exporter` liegen ausschließlich in dieser Collection. Die Rollen
entfallen aus `degit.infrastructure`. Aufrufer verwenden künftig
`degit.monitoring.alloy` bzw. `degit.monitoring.node_exporter`. Es gibt keine
Wrapper oder gegenseitigen Collection-Abhängigkeiten.

Firewall und Netzwerk bleiben bei `degit.infrastructure`. Wer die optionale
Firewall-Verwaltung einer Monitoringrolle aktiviert, installiert zusätzlich die
Host-Collection. Ohne diesen Schalter verwaltet die Monitoringrolle keine Ports.

`grafana_agent` und `promtail` sind entfernt. Die bestehenden Systeme sind bereits
umgestellt; die Collection führt weder eine Migration noch eine Deinstallation
auf Servern aus. Vier bisherige Platzhalterrollen bleiben ausdrücklich nicht
implementiert und weisen Aufrufe vor Änderungen zurück.

## Rolle und Plattform

Der generierte Einstieg lädt `tasks/preflight.yml` und anschließend die fachliche
Implementierung aus `tasks/configuration.yml`. Plattformwerte werden in der
Reihenfolge Familie, Distribution und Release geladen. Fehlende erforderliche
Facts werden nachgeladen; globale Fact-Aliase sind abgeschaltet.

Linux-Ziele sind Debian 13, Ubuntu 22.04/24.04/26.04 sowie Rocky/RHEL 9.
Windows ist ausschließlich für den getrennten Alloy-Agentpfad vorgesehen.
Diese Matrix beschreibt den Zielvertrag. Freigaben benötigen reale Diensttests
je Plattform; ein Syntaxcheck oder Rocky-Test belegt keinen Windows-/RHEL-Betrieb.

## Dienste und Konfiguration

`*_manage_service: false` verhindert Dienstaktionen durch Tasks und Handler.
`*_service_state: stopped` darf durch einen Konfigurationshandler nicht aufgehoben
werden. Die gewünschte Dienstpolicy wird im Rollenlauf für verzögerte Handler
erfasst. Bereits vorhandene Betriebsdaten werden nicht gelöscht.

Die Linux-Verbesserungen für Alloy und node_exporter wurden aus dem vorbereiteten
Host-Checkout übernommen. Alloy unterstützt eine strukturierte Konfiguration mit
`alloy_config` und ergänzenden Blöcken. Das bisherige automatische Pipelineprofil
ist mit `alloy_pipeline_enabled: true` explizit auswählbar; beide Renderer werden
nicht gleichzeitig verwendet.

Windows-Alloy verwendet standardmäßig eine bestehende Installation. Ein URL-basierter
Installer erfordert eine SHA256-Prüfsumme. Ein temporärer Konfigurationsstand wird
validiert, bevor die aktive Datei ersetzt wird. Der frühere unversionierte
Winget-Pfad entfällt.

Kundenspezifische Blackbox-Ziele und aktive POST-Testmodule sind aus den Defaults
entfernt. Ziele, Empfänger, Secrets und Alarmgrenzen stammen aus dem jeweiligen
Infrastructure-Inventory. Windows/Linux-Alarmtexte bleiben Bestandteil des
wiederverwendbaren Annotation-Filters.

## Abnahme und Rückbau

Zuerst Collection bauen und das Artefakt prüfen/installieren, danach die tatsächlichen
FQCNs testen. Negative Plattformtests müssen vor Änderungen abbrechen. Konfiguration,
Dienstzustand, zweiter Lauf und Datenpfade werden separat geprüft. Upstream-Updates
und Datenformatwechsel erhalten eine eigene Abnahme; der Gerüstumbau allein
aktualisiert keine produktiven Dienste.

Vor einem Pilotrollout bleiben das bisherige Collection-Artefakt, Inventory und
Datenbackup verfügbar. Ein Binary-Rückbau ist nur zulässig, wenn das bestehende
Datenformat kompatibel ist; andernfalls wird auf die geprüfte Sicherung zurückgegangen.

## Explizite Konfiguration

Die früheren all_/group_vars_/host_vars_-Zusammenführungen entfallen. Konfiguration
wird vollständig über prometheus_config bzw. blackbox_exporter_config übergeben;
Dateilisten über prometheus_alert_rules_files und prometheus_static_targets_files.
Inventory-Layer führen gewünschte Ergänzungen ausdrücklich zusammen.
Prometheus Remote Write ist nur mit prometheus_remote_write_receiver_enabled: true
aktiv. Öffentliche URLs und SMTP-Empfänger müssen ausdrücklich gesetzt werden.

## Native Entwicklungsabnahme

Die VM-basierte Basisabnahme und reproduzierbaren Testplaybooks sind unter
[validation/README.md](validation/README.md) dokumentiert. Das ist keine automatische
Freigabe aller Exporter, neuer Software-Majorversionen oder produktiver Datenmigrationen.

## LPM als Standard

`prometheus_lpm_enabled` und `alertmanager_lpm_enabled` sind standardmäßig aktiv.
Vor der Umstellung sind bisherige LPM-Basisregeln aus der externen Regelliste zu
entfernen. Kundeneigene Erweiterungen und Unternehmensvorlagen bleiben im
Infrastruktur-Repo. Bestehende explizite HTML-/Text-/Betreffkonfigurationen werden
beibehalten. Bei Bedarf kann jedes Backendprofil separat deaktiviert werden.

Node Exporter deaktiviert den für OOM-/Swap-Metriken benötigten `vmstat`-Collector
nicht mehr standardmäßig. Windows-Alloy aktiviert zusätzlich `memory`. Im Alloy-
Pipelineprofil kennzeichnet `alloy_lpm_enabled` die Remote-Write-Metriken für das
LPM-Scrape-Monitoring. Diese Option schaltet keine Unternehmensziele oder Empfänger ein.
