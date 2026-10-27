
## Binary provenance

Bundled binaries support Linux x86_64 and aarch64. The role rejects other
architectures before installation. `files/exporter.provenance.json` records the
immutable upstream revision, source checksum, Go toolchain, dependency lock hashes
and binary hashes. Rebuild and verify with `tools/build_exporters.py`; unknown
bundled ELF files are rejected during artifact validation.
