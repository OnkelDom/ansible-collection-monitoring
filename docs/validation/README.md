# Native Abnahme auf pve.lenmail.de

Die aktuelle Ergänzung für `degitag.monitoring:2.0.0` steht in der
[Release-Abnahme vom 27.10.2026](release-readiness-2026-10-27.md).
Der folgende historische Nachweis behält seinen ursprünglichen Umfang und Namespace.

Stand: 18.10.2026. Getestet wird der vorbereitete Branch `codex/monitoring-v2`
mit dem gebauten und installierten Artefakt `degit.monitoring:2.0.0`.
Dies ist eine Entwicklungsabnahme, kein Produktionsrelease.

## Verantwortung und Testaufbau

Sechs eigene Wegwerf-VMs (3390–3395) wurden auf ausdrückliche Freigabe angelegt.
Vorhandene Mandantenlabore und produktive Gäste wurden nicht verändert. Die fünf
Linux-Gäste stammen aus offiziellen, gegen deren veröffentlichte Checksummen
geprüften Cloud-Images: Debian 13, Ubuntu 22.04/24.04/26.04 und Rocky Linux 9.8.
Rocky läuft mit SELinux `Enforcing`. Windows 11 Enterprise Evaluation wurde frisch
installiert; es wurde kein Mandantenabbild geklont.

Jeder Linux-Gast betreibt Node Exporter, Prometheus, Alertmanager, Blackbox Exporter,
Loki, Tempo und Alloy nativ unter systemd; Grafana wird separat abgenommen.
Windows betreibt Alloy als Windows-Dienst und sendet ausschließlich an den eigenen
Debian-Testgast. Alertmanager verwendet den lokalen Blackhole-Empfänger ohne SMTP.
Es werden keine produktiven Remote-Write-, Loki-, OTLP- oder Mailziele verwendet.

## Reproduzierbare Prüfungen

Die Playbooks setzen ausdrücklich befüllte Inventories `monitoring_lab` bzw.
`monitoring_windows_lab` voraus. Sie dürfen nur auf entbehrliche Testgäste angewandt
werden. Installer-URL, Installer-SHA256 und das Grafana-Testpasswort werden über
Umgebungsvariablen übergeben; Zugangsdaten gehören in ein geschütztes temporäres
Inventory und werden nach Abschluss entfernt.

- `tests/integration/native_services.yml`: Installation der sieben Kerndienste,
  HTTP-Bereitschaft, reale Node-Metrik und lokaler Blackbox-Probe.
- `tests/integration/grafana.yml`: native Grafana-Installation und Datenbank-Health.
- `tests/integration/data_paths.yml`: Alloy Remote Write mit `platform=linux`,
  realer Journald-Eintrag über Loki und OTLP-Span mit anschließendem Tempo-Readback.
- `tests/integration/agent_lifecycle.yml`: Stop/Disable beider transferierter Agenten,
  Handlerausführung, Konfigurationsschutz, ausgeschaltete Dienstverwaltung und Start.
- `tests/integration/reboot.yml`: Gast-Neustart und Bereitschaft aller acht Dienste.
- `tests/integration/windows_alloy.yml`: SHA256-geprüfte Erstinstallation,
  Konfigurationsvalidierung, Dienststart, Bereitschaft und Windows-Application-Event.
- `tests/integration/windows_data_paths.yml`: Windows-Metriken und Application-Event
  im Linux-Testbackend, jeweils mit `platform=windows`.
- `tests/integration/windows_lifecycle.yml`: Windows-Dienststeuerung,
  Konfigurationsschutz und Bereitschaft nach Windows-Neustart.

Beispiel für einen vorhandenen Linux-Testbestand:

```bash
ansible-playbook -i /geschuetzter/pfad/lab.yml tests/integration/native_services.yml
ansible-playbook -i /geschuetzter/pfad/lab.yml tests/integration/data_paths.yml
ansible-playbook -i /geschuetzter/pfad/lab.yml tests/integration/agent_lifecycle.yml
ansible-playbook -i /geschuetzter/pfad/lab.yml tests/integration/native_services.yml
ansible-playbook -i /geschuetzter/pfad/lab.yml tests/integration/reboot.yml
```

Nach dem Lebenszyklustest stellt der native Lauf das Pipelineprofil wieder her.
Parallele Läufe mit konkurrierenden Dienst-/Konfigurationsänderungen auf demselben
Gast sind ausgeschlossen. Auf macOS benötigt WinRM gegebenenfalls
`OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` und `no_proxy='*'`, um den systemeigenen
Proxyzugriff aus Ansible-Forkprozessen zu vermeiden. Der Test-WinRM-Zugang verwendet
HTTPS mit einem temporären selbstsignierten Zertifikat; diese Laboreinstellung ist
keine Empfehlung für produktive Zertifikatsprüfung.

## Gefundene und behobene Fehler

- Der neue deb822-Repositorypfad aktualisiert nach einer Änderung die APT-Metadaten.
- Alloy und Grafana verwenden ein übereinstimmendes signiertes Paketrepository,
  damit ihre RPM-Konfigurationen einander nicht bei jedem Lauf überschreiben.
- Loki lädt und entpackt versionierte Archive auf dem Zielsystem, prüft die
  Upstream-SHA256 und installiert seine ZIP-Abhängigkeit selbst.
- Lokis lokale Ring-Adresse stimmt mit dem lokalen gRPC-Listener überein.
- Dienst-Tasks werten den gewünschten Zustand und die Startaktivierung aus.
  Verzögerte Handler verwenden die im Rollenlauf erfasste Dienstpolicy.
- Linux-Dateilogs verwenden `local.file_match`, damit nicht vorhandene optionale
  Logdateien keine fehlerhaften Tail-Quellen erzeugen.
- Windows verwendet den tatsächlichen Installer-Binärpfad
  `alloy-windows-amd64.exe`; `creates_path` verhindert erneute EXE-Installationen.

## Grenzen und Freigabe

Die genauen Ergebnisse stehen in `results.json`. Die Laufzeitabnahme umfasst acht
Linux-Rollen und Alloy auf Windows 11. Sie umfasst weder alle übrigen Exporter noch
Windows Server oder echtes RHEL. Die geprüften bestehenden Softwareversionen wurden
nicht pauschal auf neue Major-Releases angehoben. Upgrades, Datenformatwechsel,
produktiver Backup/Restore und die optionale Integration der Host-Firewall benötigen
eigene Prüfungen. Insbesondere belegt HTTP-Bereitschaft allein keine Datenaufnahme;
dafür sind die gesonderten Metrik-, Log- und Trace-Prüfungen vorgesehen.

Vor einer Produktionseinführung sind bisheriges Collection-Artefakt, Inventory und
konsistente Datenbackups zu sichern. Ein Rückbau nach einem Software-Upgrade setzt
kompatible Datenformate voraus; andernfalls ist die geprüfte Datensicherung
wiederherzustellen. Alle sechs temporären Laborgäste, Seed-ISOs, Image-Downloads und Zugangsdaten
wurden entfernt. Die Konfiguration und der Laufzustand der 14 vorhandenen Gäste
wurden vor und nach dem Rückbau verglichen und blieben unverändert. Der Abschluss
ist in `results.json` festgehalten.

Der Windows-WinRM-Testzugang war nach dem Neustart verzögert erreichbar. Während
der Diagnose erfolgte eine lokale Anmeldung; Alloy wurde dabei weder manuell
gestartet noch umkonfiguriert. Die anschließende Bereitschaftsprüfung war erfolgreich.
Dies ist kein gesonderter Nachweis eines vollständig unbeaufsichtigten
Windows-Administrationszugangs nach jedem Boot.

## Native Proxmox extension

The scoped live PVE export, central reception, dashboard and alarms are documented
in [proxmox.md](proxmox.md) and [proxmox-results.json](proxmox-results.json). This is
a separately qualified extension; older foundation/LPM artifacts retain their
original evidence scope.
