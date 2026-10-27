## Reproduzierbare Releases

Die Rolle prüft Archiv und Binärinhalt bei jedem Lauf. Sie verlässt sich nicht auf
`--version`: Upstream 2.1.4 liefert dort eine leere Versionsnummer. Ab 2.1.4 werden
die modernen Tar-Archive samt versionsbenannter Checksum-Datei verwendet; 2.1.3
verwendet das Legacy-Gzip. Der geschützte, root-eigene Releasecache behält Archive
und entpackte Dateien, sodass Wiederholungen keine Downloads neu erzeugen müssen.
Die native Abnahme prüft 2.1.3 → 2.2.0 → 2.1.3 anhand des Inhalts der jeweils
checksum-geprüften Quelle sowie der tatsächlichen Exposition. Ein echter
UniFi-Controller ist für eine kundenspezifische Backend-Abnahme zusätzlich nötig.

Versionen 2.1.4 und 2.1.5 werden vor Änderungen abgewiesen: das offizielle Binary stürzt im
Datadog-Plugin mit einem Nil-Pointer ab. Die [Upstream-Release-Notizen für 2.2.0](https://github.com/unpoller/unpoller/releases/tag/v2.2.0)
dokumentieren den Fix. Ein deaktivierter Datadog-Abschnitt behebt diese Abstürze nicht.
