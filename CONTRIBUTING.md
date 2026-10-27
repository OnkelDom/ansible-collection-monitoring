# Mitarbeit

Der verbindliche Entwicklungsvertrag steht in [docs/repository-standard.md](docs/repository-standard.md). Änderungen bleiben auf die zuständige Collection begrenzt; gemeinsame Werkzeuge werden vor einer Änderung mit den anderen Collection-Verantwortlichen abgestimmt.

## Lokale Umgebung

Auf macOS verwendet der Controller Homebrew Python 3.12 ohne sudo:

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
make prepare
```

Konfiguration bei Bedarf mit `vim ansible.cfg` bearbeiten. Rollen verwenden `ansible_facts`, geschichtete Plattformvariablen und öffentliche, typisierte Defaults. Nach Strukturänderungen:

```bash
.venv/bin/python tools/generate_role_scaffold.py
.venv/bin/python tools/format_yaml.py
make test
```

`make test` und `make ci` rufen denselben vollständigen Prüfeinstieg wie GitHub Actions auf. LPM-/Proxmox-Regelprüfungen verwenden SHA256-geprüfte Upstream-CLI-Werkzeuge. Der erste Lauf benötigt Netzwerkzugriff; heruntergeladene Archive liegen anschließend unter `.ansible/monitoring-tools`.

## Review und Abnahme

Ein Pull Request beschreibt Problem, resultierendes Verhalten und belegte Tests. Öffentliche API-/Namespace-Änderungen gehören in `docs/migration.md` und `CHANGELOG.md`. Die Collection wird vor Syntax- und Preflight-Tests gebaut, geprüft und separat installiert. Gebündelte Exporter benötigen gesperrte Quellen/Abhängigkeiten, Herkunftsnachweis und reproduzierbare Builds mit `tools/build_exporters.py`.

Native Tests unter `tests/integration/` sind ausschließlich für dedizierte, entbehrliche Testsysteme vorgesehen. Datenfluss, Idempotenz, Lifecycle, SELinux, Reboot, Versionswechsel und Restore werden getrennt von Controllerchecks nachgewiesen. Neue Nachweise in `docs/validation/` nennen Datum, Plattform, Artefakt und konkrete Grenzen; historische Berichte werden nicht umetikettiert. Ein grüner Controllercheck ist keine Freigabe für beliebige produktive Upgrades.

## Release

Ein Release benötigt einen expliziten `v<Version>`-Tag passend zu `galaxy.yml` und erfolgreiche Checks. Die Release-Pipeline hängt das konkret geprüfte Paket an GitHub an. Eine Entwicklung, ein PR oder ein Testlauf führt weder ein Deployment noch eine automatische Galaxy-Publikation aus.
