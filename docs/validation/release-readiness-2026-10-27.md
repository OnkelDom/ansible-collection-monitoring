# Release-Abnahme `degitag.monitoring:2.0.0`

Diese Abnahme ergänzt die unveränderten historischen Nachweise. Sie trennt den
Collection-Vertrag, native Laufzeit und konkrete Wartungspfade. Der Release löst
keinen Produktionsrollout und keine Galaxy-Publikation aus. Die maschinenlesbaren
Ergebnisse und Fingerprints stehen in [release-readiness-2026-10-27.json](release-readiness-2026-10-27.json).

## Architektur und gemeinsamer Repository-Vertrag

Infrastructure koordinierte den Abgleich der fünf Collections vor den Änderungen.
Jeder Verantwortliche bearbeitete sein Repository. Die acht gemeinsamen Dateien
sind bytegleich; ihre Hashes stehen im [Strukturnachweis](repository-standard-2026-10-27.json).
README-Gliederung, Make-Ziele, Prüfeinstieg, Artefaktgrenzen und CI-/Release-Vertrag
folgen `degitag-collections-v1`. Der GitHub-Remote bleibt bei OnkelDom.

Die Collection besitzt 21 implementierte Rollen. Die vier nicht implementierten
Platzhalter werden nicht ausgeliefert. Alloy und Node Exporter gehören hierher;
Telegraf und additive Host-Firewall bleiben bei Infrastructure. Für die native
Telegraf-/Firewall-Abnahme wurde ein separat gebautes Infrastructure-Artefakt
installiert. Dessen Fingerprint ist im Ergebnisnachweis festgehalten. Der ergänzende
Infrastructure-Patch 2.0.1 repariert fehlende oder leere Debian-Keyrings und
überspringt die Schlüsselkonvertierung bei identischen Folgeläufen; dieser
Cross-Collection-Vertrag wurde auf allen fünf Linux-Gästen nochmals nativ geprüft.

## Prüfmatrix

| Ebene | Prüfgegenstand |
| --- | --- |
| Controller | Python 3.12, Core 2.20/2.21 über dieselbe CI; Repository-/Scaffold-Vertrag, 49 Unitprüfungen, YAML, sämtliche Rollen-/Integration-Syntax, Production-Lint, Artefaktinstallation, Preflights, Sanity compile/import |
| LPM | 42 Recording Rules, 53 Alarme, 135 Promtool-Szenarien, 25 echte Alertmanager-Inhibitionstests und sieben Benachrichtigungsfälle |
| Linux | Debian 13, Rocky 9.8, Ubuntu 22.04/24.04/26.04; Installation der 21 Rollen, reale HTTP-/Dienstbereitschaft und wiederholte Konfiguration |
| Backends | Reale Redis-/PostgreSQL-/Squid-/Unbound-Fixtures; Vector-Konfigurationsprüfung; Telegraf-Exposition und neun normalisierte LPM-Metriken je Linux-Plattform |
| Datenpfade | Alloy Remote Write → Prometheus, Journal → Loki, OTLP → Tempo mit anschließendem Readback |
| Lebenszyklus | Stop/Disable, verzögerte Handler, ungültige Alloy-Konfiguration, ausgeschaltete Dienstverwaltung, Wiederanlauf und Gastneustart |
| Firewall | Additive UFW- bzw. permanente firewalld-Rich-Rules für Alloy/Node Exporter; SSH bleibt erreichbar |
| Windows | Frisches Microsoft Windows Server 2025 Evaluation, SHA256-geprüftes Alloy 1.21.2, Windows-Metriken und Application-Event im eigenen Linux-Sink, Dienstpolicy, Konfigurationsschutz und unbeaufsichtigter WinRM-/Alloy-Wiederanlauf nach Reboot; Wiederholung `changed=0` |

Die Hauptmatrix verwendete sechs eigens erzeugte Wegwerf-VMs auf
`pve.lenmail.de`, IDs 3390–3395. Ein zusätzlicher frischer Debian-Kontrollgast
3396 prüfte Grafanas Bootstrap samt authentifiziertem Dashboardzugriff. Linux-Cloud-Images wurden gegen veröffentlichte SHA256/SHA512 geprüft;
Windows stammt aus Microsofts Evaluation-VHDX. Es wurden keine Mandantengäste
geklont. Alertmanager verwendete ausschließlich Blackhole-Empfänger, sämtliche
Telemetryziele gehörten zum Testbestand. Das Testinventory, temporäre Schlüssel,
Passwörter und Seed-Medien gehören nicht ins Repository.

## Versionswechsel und Datenwiederherstellung

Auf Debian 13 wurden die folgenden konkreten Versionspaare in beide Richtungen
mit den öffentlichen Rollenvariablen angewandt; nach jeder Phase wurden die
installierte Version bzw. der Inhalt des checksum-geprüften Releaseartefakts und
die reale Exposition geprüft:

| Rolle | Basis → Kandidat → Basis |
| --- | --- |
| Consul Exporter | 0.7.1 → 0.8.0 → 0.7.1 |
| Redis Exporter | 1.46.0 → 1.47.0 → 1.46.0 |
| Process Exporter | 0.7.5 → 0.8.1 → 0.7.5 |
| SNMP Exporter | 0.18.0 → 0.19.0 → 0.18.0 |
| Systemd Exporter | 0.4.0 → 0.5.0 → 0.4.0 |
| Pushgateway | 1.4.3 → 1.5.1 → 1.4.3 |
| VictoriaMetrics | 1.57.1 → 1.58.0 → 1.57.1 |
| UniFi Poller | 2.1.3 → 2.2.0 → 2.1.3 |

Ein persistenter VictoriaMetrics-Probewert prüft den Versionsrundlauf. Process
Exporter 0.8.0 wird wegen seines defekten Upstream-Listeners vor Änderungen
abgewiesen. Systemd-Exporter-Flags und Unpoller-Archivnamen werden passend zur
Version ausgewählt. Unpoller 2.1.4/2.1.5 werden wegen bestätigter Upstream-Abstürze
abgewiesen; 2.2.0 enthält einen weiteren Datadog-Fix. Unpoller 2.1.4 enthält keine Versionsmetadaten; dessen
Binärinhalt wird deshalb gegen die entpackte verifizierte Quelle verglichen. Linux-Paketdefaults für Alloy/Grafana sowie Vector sind
konkret festgelegt. Windows `creates_path` qualifiziert die Erstinstallation;
eine geänderte EXE-URL ist kein zugesicherter In-place-Upgradepfad.

Der Cold-Restore-Test stoppt Alloy und sieben persistente Backends, sichert deren
acht Datenverzeichnisse, entfernt diese ausdrücklich nur auf markierten
Wegwerfgästen und stellt sie aus dem Archiv wieder her. Vor dem Start werden alle
regulären Dateien mit SHA256 bytegleich verglichen. Anschließend werden der
historische Prometheus-Wert, die vorherige Loki-Journalmeldung, der ursprüngliche
Tempo-Trace und eine persistierte Alertmanager-Silence geprüft. Der Gastneustart
prüft zusätzlich alle 21 Monitoringdienste und Telegraf.

## Exporter-Herkunft und behobene Laufzeitfehler

iLO5, Squid und Unbound wurden aus unveränderlichen Upstream-Commits mit gesperrten,
aktualisierten Go-Modulen für Linux AMD64 und ARM64 neu gebaut. Manifest, Lizenz,
Quell-/Patch-/Modulhashes und Binärhashes werden geprüft. Ein zweiter vollständiger
Build erzeugte identische Binärhashes. Native Go-Tests prüfen Unbound-Blocklisten
und den modernen Squid-Manager-Pfad. `govulncheck -mode=binary` fand in den drei
AMD64-Binärdateien keine bekannten Schwachstellen zum Abnahmezeitpunkt.

Die native Matrix korrigierte außerdem Grafanas Dateirechte und die versehentliche
Provisionierung von Provenienz-/opt-in-PVE-Dateien im allgemeinen Provider sowie
controllerseitige sudo-Downloads,
ignorierte Versionsparameter, falsche Checksum-Dateinamen, einen gemeinsamen
Systemd-Exporter-Benutzer, SNMP-Konfigurationsaktivierung und Unbounds Socketpfade.
Auf Ubuntu 22.04 aktiviert das Testfixture den Control-Socket explizit; die
Exporter-Rolle verändert den DNS-Dienst selbst nicht. Der Squid-Patch liest auch
Squid 7 über `/squid-internal-mgr/counters` aus. Unbounds optionale Blockliste
funktioniert ohne Header oder abschließenden Zeilenumbruch.

## LPM-Vertrag und Prüfgrenzen

Die [Quellenmatrix](../../roles/prometheus/files/lpm/source-matrix.yml) beschreibt
metrische Einheiten, Labels, high/mid/low-Schwellen und optionale Fähigkeiten.
Node-Familien haben pro Host/Ressource Vorrang vor Telegraf; Quellen werden nicht
zusammengemittelt. Telegraf-Diskzeiten werden von Millisekunden korrekt umgerechnet.
Verfügbare Speicherkapazität berücksichtigt wiederverwendbaren Cache. Entfernte
Mounts, Nullkapazitäten, Counter-Resets, Windows-Varianten, OOM-Haltezeiten,
ausgewählte Dienste und optionale Port-/HTTP-Probes sind semantisch geprüft.

WARN wird nur durch ERROR derselben Identität, Familie und Ressource inhibiert.
Unterschiedliche Mandanten, Plattformen, Klassen, Laufwerke, Schnittstellen,
Dienste und Probeziele unterdrücken einander nicht. Collector-Ausfall unterdrückt
abhängige Folgemeldungen innerhalb derselben Hostidentität. Fehlende optionale
Collector erzeugen keine erfundene Aussage. Ein stiller Remote-Write-Agent
benötigt eine extern definierte Erwartung/Heartbeat; Basistelegraf liefert keine
PSI-Daten. SMTP-Zustellung an echte Empfänger gehört nicht zu dieser Blackhole-Abnahme.

Rocky 9 ersetzt auf Nutzerwunsch die native RHEL-Abnahme; ein abonniertes RHEL 9
wurde nicht separat getestet. ARM64 ist reproduzierbar gebaut, aber nicht nativ
abgenommen. iLO-Hardware, echte UniFi-Controller, externe Consul-Server und
SNMP-Geräte standen nicht zur Verfügung; deren Exporter wurden als Dienste und
Exposer geprüft. Die realen Backend-Fixtures ersetzen keine kundenspezifischen
Berechtigungs-, Zertifikats- oder Inventartests. Ebenso sind die genannten
Versionspaare und Cold-Restores keine Zusage beliebiger Major-Downgrades oder
plattformübergreifender Datenformatkompatibilität. Produktive Einführung bleibt
ein eigener Auftrag mit passender Datensicherung und Betreiber-Inventory.

## Laborabschluss

Alle sieben eigenen Gäste 3390–3396, ihre Datenträger, Image-Downloads und Seed-ISOs
wurden entfernt. Die Identität, der Knoten und der Laufzustand der 15 vorbestehenden
Gäste entsprechen dem Zustand vor Testbeginn; während des Rückbaus blieben auch
deren Konfigurationshashes unverändert. Temporäre Testzugänge werden nicht
weiterverwendet. Qualifizierte Logs und Artefakte bleiben lokal unter
`.git/qualification-evidence/2026-10-27/` erhalten; ihre Hashes stehen im JSON-Nachweis.
