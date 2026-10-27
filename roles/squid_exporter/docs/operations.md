
## Binary provenance

Bundled binaries support Linux x86_64 and aarch64. The role rejects other
architectures before installation. `files/exporter.provenance.json` records the
immutable upstream revision, source checksum, Go toolchain, dependency lock hashes
and binary hashes. Rebuild and verify with `tools/build_exporters.py`; unknown
bundled ELF files are rejected during artifact validation.


`squid_exporter_version` ist für das gebündelte, überprüfte Artefakt auf 1.8.2
begrenzt. Andere Quellen erfordern einen bewussten Neubau mit neuer Provenienz;
eine abweichende Versionsnummer wird nicht stillschweigend ignoriert.

Der gebündelte Patch verwendet `/squid-internal-mgr/counters`, damit auch Squid 7
auf Ubuntu 26.04 ausgelesen wird. Ein echter HTTP-Fixturetest prüft den Pfad und
das Parsen; die native Matrix prüft `squid_up=1` gegen lokale Squid-Backends.
