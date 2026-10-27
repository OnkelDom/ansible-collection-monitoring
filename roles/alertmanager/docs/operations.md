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


## LPM-Inhibition und Ressourcengrenzen

ERROR unterdrückt WARN nur innerhalb derselben LPM-Alarmfamilie und identischen
Instanz-, Mandanten-, Umgebungs-, Standort- und Plattformgrenzen. Dateisystem,
Gerät, I/O-Name, Interface, Probe-Ziel, Server/Port/Protokoll/Methode und Klasse
müssen ebenfalls übereinstimmen. Unterschiedliche Datenträger oder Ziele werden
nicht gegenseitig unterdrückt. Eine leere Instanzkennung ist keine gemeinsame
Hostidentität und erhält keine Severity-Inhibition.

Ein ausdrücklich markierter `LPMCollectorDown` unterdrückt Ressourcenfolgealarme
nur für dieselbe Instanz und denselben Mandanten/Standort/dieselbe Plattform;
Verfügbarkeitsalarme bleiben davon ausgenommen. Dafür müssen direkte Scrapes neben
`monitoring_profile="lpm"` auch `platform="linux"` bzw. `"windows"` tragen.
Komplett verlorene Remote-Write-Sender benötigen zusätzlich externes Heartbeat.

Die Standardregeln gelten unabhängig davon, ob Alloy, Node Exporter oder Telegraf
die vereinbarten LPM-Messwerte liefert. Eigene Regeln in
`alertmanager_inhibit_rules` werden zusätzlich angewendet. Der lokale Prüfeinstieg
startet einen isolierten echten Alertmanager mit Blackhole-Empfänger und prüft
positive sowie negative Inhibition-Fälle. Es wird keine Testmail versendet.
