
## Binary provenance

Bundled binaries support Linux x86_64 and aarch64. The role rejects other
architectures before installation. `files/exporter.provenance.json` records the
immutable upstream revision, source checksum, Go toolchain, dependency lock hashes
and binary hashes. Rebuild and verify with `tools/build_exporters.py`; unknown
bundled ELF files are rejected during artifact validation.


## Unbound-Steuerpfad und optionale Blockliste

Die Plattformschicht wählt den Paketstandard für den lokalen Unix-Control-Socket:
Debian/Ubuntu `/run/unbound.ctl`, Rocky/RHEL `/run/unbound/control`. Abweichende
Installationen überschreiben `unbound_exporter_config_flags_extra['unbound.uri']`.
Auf Ubuntu 22.04 muss der Betreiber Control explizit aktivieren; die Exporter-Rolle
konfiguriert den DNS-Dienst nicht selbst.
TCP-Control benötigt entsprechend konfigurierte Zertifikate und Serverfreigaben.

Blocklisten-Metriken sind optional; ein Dateipfad wird ausdrücklich über
`unbound_exporter_config_flags_extra['block-file']` angegeben. Der geprüfte
Source-Patch zählt eindeutige Domains aus `local-zone`/`local-data`, unterstützt
Dateien ohne Header oder abschließenden Zeilenumbruch und liefert keine negativen
Anzahlen. Die Herkunftsdatei verweist auf Patch und Go-Regressionstest.
