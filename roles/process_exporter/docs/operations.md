## Versionsvertrag

Archive werden auf dem Ziel gegen die veröffentlichte Prüfsumme geprüft. Die native
Release-Abnahme umfasst den Wechsel 0.7.5 → 0.8.1 → 0.7.5. Version 0.8.0 wird vor
Änderungen abgewiesen: deren Upstream-Implementierung übergibt keine Listen-Adresse
an das Exporter-Toolkit und startet deshalb keinen HTTP-Listener. Die Korrektur
steht in [Upstream 0.8.1](https://github.com/ncabatoff/process-exporter/blob/v0.8.1/cmd/process-exporter/main.go).
Andere Versionen benötigen eine eigene Laufzeitprüfung.
