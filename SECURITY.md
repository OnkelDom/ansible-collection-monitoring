# Sicherheit

Sicherheitslücken vertraulich über das Security Advisory des tatsächlichen GitHub-Repositories melden. Falls dieser Kanal nicht verfügbar ist, zunächst den Maintainer über die Kontaktadresse in `galaxy.yml` kontaktieren. Öffentliche Issues enthalten keine ausnutzbaren Details, Zugangsdaten oder produktiven Hostdaten.

Secrets werden über Ansible Vault oder einen Secret Store im Betreiber-Inventory bereitgestellt. Sie gehören weder in Defaults, Beispiele, Tests, Logs noch in Collection-Artefakte. Testkonten und temporäre Labordaten sind nach der Abnahme zu entfernen. Für produktive Endpunkte sind TLS und Zertifikatsprüfung entsprechend dem jeweiligen Dienst einzurichten.

Upstream-Archive werden mit SHA256 geprüft. Die zusätzlich gebündelten Exporter besitzen Herkunftsdateien, gesperrte Buildabhängigkeiten und Binärprüfsummen. Verdächtige Dateien oder abweichende Prüfsummen blockieren den Build; sie werden nicht durch Abschalten der Prüfung akzeptiert.

Die Vorbereitung von Version 2.0.0 ist noch kein veröffentlichtes Produktionsrelease. Unterstützte Plattformen und konkrete Laufzeitnachweise stehen in README und `docs/validation/`; Release- und Upgradeentscheidungen berücksichtigen deren tatsächlichen Umfang.
