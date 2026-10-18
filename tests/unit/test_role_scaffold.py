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
