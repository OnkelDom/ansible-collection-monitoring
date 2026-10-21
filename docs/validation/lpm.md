# LPM-Standardprofil: Entwicklungsabnahme

Stand: 18.10.2026, Branch `codex/monitoring-v2`, Collection `degit.monitoring:2.0.0`.
Verantwortung: Die Collection besitzt neutrale Host-Regeln und Darstellung; das
Infrastructure-Inventory besitzt Mandantenkennzeichen, Ziele, SMTP, Empfänger,
Unternehmensbranding und anwendungsspezifische Betriebsregeln.

## Prüfumfang

- 63 gebündelte Regeln: 34 Recording Rules und 29 Alarme.
- Promtool-Fälle für Node Exporter, Windows Exporter und beide Alloy-Metrikfamilien
  mit beliebigen Jobnamen, fehlender/gesetzter Kritikalität und getrennten Mandanten.
- Windows-Bootzeitnamen aus drei Exporter-Generationen; keine Division durch null
  auf Windows-Volumes ohne Kapazität.
- Alarmauslösung und Haltezeit, insbesondere die Stunde für Klasse `low`;
  Scrape-Ausfälle nur für ausdrücklich als LPM markierte Ziele.
- Windows-Alarmtext wird durch Promtool tatsächlich gerendert und mit vollständigen
  erwarteten Annotationen verglichen; er enthält den passenden PowerShell-Befehl.
- Sieben Mailfälle: kritisch, Linux, Windows, Entwarnung, gemischt, fehlende Labels
  und HTML-Escaping; jeweils Betreff, Text und HTML mit echtem `amtool` gerendert.
- Unit-Prüfungen verhindern Kundennamen/-domains im gebündelten Profil und prüfen
  die Priorität expliziter kundeneigener Mailinhalte.

Die CLI-Prüfer stammen aus den offiziellen Upstream-Releases. Der Downloadhelfer
prüft SHA256; getestet wird mit Prometheus/Promtool 2.48.0 und Alertmanager/Amtool
0.27.0 passend zu den derzeitigen Rollen-Defaults. CI führt dieselben semantischen
Prüfungen für Core 2.20/2.21 aus, sobald dieser Branch veröffentlicht wird.

```bash
python tests/install_monitoring_test_tools.py --dest /tmp/monitoring-tools
python tests/run_lpm_checks.py --promtool /tmp/monitoring-tools/promtool --amtool /tmp/monitoring-tools/amtool
```

## Native Abnahme

Eine eigene temporäre Debian-13-VM auf `pve.lenmail.de` führt das gebaute/installierte
Collection-Artefakt mit den FQCNs aus. Sie lädt zusätzlich eine unabhängig verwaltete
Testregel und betreibt Node Exporter sowie den Alloy-Remote-Write-Pfad. Die neun
Regelgruppen einschließlich der Fremdregel müssen nach ihrer ersten Auswertung
vollständig `health=ok` melden.

Der Test lädt außerdem eine neutrale Mailroute mit reservierten `.invalid`-Adressen.
Sie ist ausschließlich über einen nie verwendeten Testmatcher erreichbar. Alle
Testalarme laufen in den Blackhole-Empfänger. Es wird keine Mail versendet und kein
produktiver Collector oder Alarmmanager geändert.

`tests/integration/lpm_profile.yml` prüft die tatsächliche Alertmanager-Konfiguration,
Metriknormalisierung, die installierten Dateien sowie künstliche ERROR-/WARN-Paare.
Die Unterdrückung muss andere Mandanten, Pfade und Alarmfamilien unberührt lassen.
Ein deaktiviertes Profil muss seine eigenen Dateien entfernen und die separat
verwaltete Testregel erhalten; anschließend wird es wieder aktiviert.

## Grenzen und Rückbau

Die neuen Windows-Regeln sind mit synthetischen Exporter-Zeitreihen und echten
Promtool-Annotationen geprüft. Für diese Ergänzung wurde keine neue Windows-VM
installiert; die vorherige native Alloy-Abnahme ist separat dokumentiert. Ein
SMTP-/Postfachnachweis gehört nicht zu den Renderprüfungen.

Vor einem Rollout sind alte LPM-Doppeldefinitionen aus dem Kunden-Inventory zu
entfernen, die realen Ressourcenklassen und Empfänger zu prüfen und die aktuelle
Collection-/Inventory-Version zu sichern. Die beiden `*_lpm_enabled`-Schalter
deaktivieren die jeweils verwaltete Basis; eigene Regeln, Vorlagen und Business-
Erweiterungen bleiben außerhalb dieser Besitzgrenze. Upgrades und Betriebsdaten-
Restore bleiben eigenständige Freigaben.

## Abschluss

Aktivierung, Deaktivierung, Wiederherstellung, Ressourcen-/Mandanten-/Familiengrenzen
und Wiederholungslauf wurden erfolgreich geprüft (`changed=0`). Die eigene VM 3390,
das Seed-ISO und der Image-Download wurden entfernt. Die Konfiguration und der
Laufzustand der 14 vorhandenen Gäste blieben beim Rückbau unverändert. Ergebnisse
und Artefakt-SHA256 stehen in `lpm-results.json`.
