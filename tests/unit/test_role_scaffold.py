from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.generate_role_scaffold import build_role_files, iter_role_dirs, load_config  # noqa: E402


def test_generated_role_files_are_current() -> None:
    config = load_config()

    for role_dir in iter_role_dirs():
        generated = build_role_files(config, role_dir)
        for path, expected in generated.items():
            assert path.exists(), f"Missing generated file: {path}"
            assert path.read_text(encoding="utf-8") == f"{expected.rstrip()}\n"


def test_generation_retains_operating_instructions(tmp_path) -> None:
    role = tmp_path / "prometheus"
    (role / "docs").mkdir(parents=True)
    note = "## Operating instructions\n\nKeep data on the dedicated volume.\n"
    (role / "docs" / "operations.md").write_text(note, encoding="utf-8")
    readme = build_role_files(load_config(), role)[role / "README.md"]
    assert "## Example Playbook" in readme
    assert readme.endswith(note)
    (role / "README.md").write_text(readme, encoding="utf-8")
    assert build_role_files(load_config(), role)[role / "README.md"] == readme


def test_new_role_has_real_entry_and_platform_layers(tmp_path):
    role = tmp_path / 'sample'
    role.mkdir()
    generated = build_role_files(load_config(), role)
    for name in ['tasks/main.yml', 'tasks/preflight.yml', 'tasks/configuration.yml', 'vars/platform/Debian.yml', 'vars/platform/Ubuntu-26.04.yml']:
        assert role / name in generated


def test_tests_reference_installed_collection():
    import yaml
    config = load_config()
    for role in iter_role_dirs():
        files = build_role_files(config, role)
        play = yaml.safe_load(files[role / 'tests/test.yml'])[0]
        assert play['roles'][0]['role'] == 'degitag.monitoring.' + role.name


def test_retired_agents_are_not_shipped():
    assert not (ROOT / 'roles/grafana_agent').exists()
    assert not (ROOT / 'roles/promtail').exists()
