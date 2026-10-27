from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
ROLES_DIR = ROOT / "roles"
SCAFFOLD_CONFIG = yaml.safe_load((ROOT / "tools" / "role_scaffold_config.yml").read_text(encoding="utf-8"))
REQUIRED_FILES = (
    Path("README.md"),
    Path("defaults/main.yml"),
    Path("tasks/main.yml"),
    Path("tasks/preflight.yml"),
    Path("tasks/configuration.yml"),
    Path("meta/main.yml"),
    Path("meta/argument_specs.yml"),
    Path("tests/test.yml"),
)


def test_roles_follow_required_file_conventions() -> None:
    missing: list[str] = []

    for role_dir in sorted(path for path in ROLES_DIR.iterdir() if path.is_dir()):
        for relative_path in REQUIRED_FILES:
            target = role_dir / relative_path
            if not target.exists():
                missing.append(f"{role_dir.name}: missing {relative_path}")

    assert not missing, "\n".join(missing)


def test_role_directory_names_use_underscores_only() -> None:
    invalid = sorted(path.name for path in ROLES_DIR.iterdir() if path.is_dir() and "-" in path.name)
    assert not invalid, f"Role directories must use underscores instead of hyphens: {', '.join(invalid)}"


def test_role_test_playbooks_gather_facts() -> None:
    invalid: list[str] = []

    for role_dir in sorted(path for path in ROLES_DIR.iterdir() if path.is_dir()):
        test_playbook = role_dir / "tests" / "test.yml"
        content = yaml.safe_load(test_playbook.read_text(encoding="utf-8"))

        if not isinstance(content, list) or not content:
            invalid.append(f"{role_dir.name}: tests/test.yml must contain at least one play")
            continue

        first_play = content[0]
        if not isinstance(first_play, dict) or first_play.get("gather_facts") is not True:
            invalid.append(f"{role_dir.name}: tests/test.yml must set gather_facts: true")

    assert not invalid, "\n".join(invalid)


def test_roles_using_ansible_facts_have_fact_aware_syntax_playbooks() -> None:
    invalid: list[str] = []

    for role_dir in sorted(path for path in ROLES_DIR.iterdir() if path.is_dir()):
        task_files = list((role_dir / "tasks").glob("*.yml"))
        uses_ansible_facts = any("ansible_" in path.read_text(encoding="utf-8") for path in task_files)
        if not uses_ansible_facts:
            continue

        test_playbook = role_dir / "tests" / "test.yml"
        content = yaml.safe_load(test_playbook.read_text(encoding="utf-8"))
        first_play = content[0] if isinstance(content, list) and content else {}
        if not isinstance(first_play, dict) or first_play.get("gather_facts") is not True:
            invalid.append(f"{role_dir.name}: uses ansible facts in tasks but tests/test.yml does not gather facts")

    assert not invalid, "\n".join(invalid)


def test_role_readmes_include_core_sections_and_examples() -> None:
    invalid: list[str] = []

    for role_dir in sorted(path for path in ROLES_DIR.iterdir() if path.is_dir()):
        readme = role_dir / "README.md"
        text = readme.read_text(encoding="utf-8")

        for section in ("## Supported platforms", "## Role Variables", "## Example Playbook", "## Testing"):
            if section not in text:
                invalid.append(f"{role_dir.name}: README.md missing section {section}")

        if "```yaml" not in text:
            invalid.append(f"{role_dir.name}: README.md must contain at least one YAML example block")

        if f"degitag.monitoring.{role_dir.name}" not in text:
            invalid.append(f"{role_dir.name}: README.md example playbook must reference degitag.monitoring.{role_dir.name}")

    assert not invalid, "\n".join(invalid)


def test_argument_specs_cover_all_default_variables() -> None:
    invalid: list[str] = []

    for role_dir in sorted(path for path in ROLES_DIR.iterdir() if path.is_dir()):
        defaults = yaml.safe_load((role_dir / "defaults" / "main.yml").read_text(encoding="utf-8")) or {}
        specs = (
            yaml.safe_load((role_dir / "meta" / "argument_specs.yml").read_text(encoding="utf-8")) or {}
        ).get("argument_specs", {}).get("main", {}).get("options", {})

        missing = sorted(key for key in defaults if key not in specs)
        if missing:
            invalid.append(f"{role_dir.name}: meta/argument_specs.yml missing defaults {', '.join(missing)}")

    assert not invalid, "\n".join(invalid)


def test_role_meta_main_matches_collection_quality_baseline() -> None:
    invalid: list[str] = []
    common_platforms = SCAFFOLD_CONFIG["common_platforms"]
    platform_overrides = SCAFFOLD_CONFIG.get("role_platform_overrides", {})
    min_ansible_version = str(SCAFFOLD_CONFIG["min_ansible_version"])

    for role_dir in sorted(path for path in ROLES_DIR.iterdir() if path.is_dir()):
        meta = yaml.safe_load((role_dir / "meta" / "main.yml").read_text(encoding="utf-8")) or {}
        galaxy_info = meta.get("galaxy_info", {})
        expected_platforms = platform_overrides.get(role_dir.name, common_platforms)

        if str(galaxy_info.get("min_ansible_version")) != min_ansible_version:
            invalid.append(f"{role_dir.name}: meta/main.yml has unexpected min_ansible_version")

        if galaxy_info.get("license") != SCAFFOLD_CONFIG.get("role_licenses", {}).get(role_dir.name, "MIT"):
            invalid.append(f"{role_dir.name}: meta/main.yml must preserve its configured license")

        dependencies = meta.get("dependencies")
        if not isinstance(dependencies, list):
            invalid.append(f"{role_dir.name}: meta/main.yml dependencies must be a list")

        actual_platforms = galaxy_info.get("platforms")
        expected = [
            {"name": item["name"], "versions": [str(version) for version in item["versions"]]}
            for item in expected_platforms
        ]
        if actual_platforms != expected:
            invalid.append(f"{role_dir.name}: meta/main.yml platforms do not match scaffold config")

    assert not invalid, "\n".join(invalid)
