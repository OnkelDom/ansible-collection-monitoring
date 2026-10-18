#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import io
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml
from ruamel.yaml import YAML


ROOT = Path(__file__).resolve().parents[1]
ROLES_DIR = ROOT / "roles"
CONFIG_PATH = ROOT / "tools" / "role_scaffold_config.yml"


def yaml_dump(data: Any) -> str:
    formatter = YAML()
    formatter.explicit_start = True
    formatter.default_flow_style = False
    formatter.allow_unicode = False
    formatter.sort_base_mapping_type_on_output = False
    formatter.indent(mapping=2, sequence=2, offset=0)
    formatter.width = 1000

    buffer = io.StringIO()
    formatter.dump(data, buffer)
    return buffer.getvalue()


def load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        return None
    return yaml.safe_load(content)


def load_config() -> dict[str, Any]:
    config = load_yaml(CONFIG_PATH)
    if not isinstance(config, dict):
        raise ValueError(f"Invalid scaffold config: {CONFIG_PATH}")
    return config


def infer_type(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return "str"


def infer_elements(value: Any) -> str | None:
    if not isinstance(value, list) or not value:
        return None
    first = value[0]
    value_type = infer_type(first)
    return value_type if value_type != "float" else "raw"


def get_platforms(config: dict[str, Any], role_name: str) -> list[dict[str, Any]]:
    return deepcopy(config.get("role_platform_overrides", {}).get(role_name, config["common_platforms"]))


def format_platform_list(platforms: list[dict[str, Any]]) -> str:
    return "\n".join(f"- {item['display']}" for item in platforms)


def render_defaults_block(defaults: Any) -> str:
    if defaults in (None, {}):
        return "This role does not define defaults in `defaults/main.yml`.\n"

    dumped = yaml_dump(defaults).strip()
    return f"```yaml\n{dumped}\n```\n"


def build_meta_main(config: dict[str, Any], role_name: str, description: str) -> str:
    platforms = get_platforms(config, role_name)
    data = {
        "galaxy_info": {
            "author": "Dominik Lenhardt",
            "description": description,
            "license": "MIT",
            "min_ansible_version": config["min_ansible_version"],
            "platforms": [
                {
                    "name": platform["name"],
                    "versions": [str(version) for version in platform["versions"]],
                }
                for platform in platforms
            ],
            "galaxy_tags": ["linux", "system", "infrastructure"],
        },
        "dependencies": [],
    }
    return yaml_dump(data)


def build_argument_specs(role_name: str, defaults: Any) -> str:
    options: dict[str, Any] = {}
    if isinstance(defaults, dict):
        for variable_name, value in defaults.items():
            entry: dict[str, Any] = {
                "description": [f"Controls `{variable_name}` for the `{role_name}` role."],
                "required": False,
                "type": infer_type(value),
            }
            elements = infer_elements(value)
            if elements:
                entry["elements"] = elements
            options[variable_name] = entry

    data = {
        "argument_specs": {
            "main": {
                "short_description": f"Entry point for the {role_name} role.",
                "description": [f"Validate variables for the `{role_name}` role."],
                "options": options,
            }
        }
    }
    return yaml_dump(data)


def build_role_readme(config: dict[str, Any], role_name: str, description: str, defaults: Any) -> str:
    collection = f"{config['collection_namespace']}.{config['collection_name']}"
    platforms = get_platforms(config, role_name)
    defaults_block = render_defaults_block(defaults)
    return f"""# {role_name}

{description}

## Supported platforms

{format_platform_list(platforms)}

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

{defaults_block}
## Example Playbook

```yaml
- name: Apply {role_name}
  hosts: all
  become: true
  roles:
    - role: {collection}.{role_name}
```

## Testing

The collection CI runs `ansible-lint`, `ansible-test sanity`, repository consistency tests, and per-role syntax checks using `roles/{role_name}/tests/test.yml`.
"""


def build_role_test_playbook(config: dict[str, Any], role_name: str) -> str:
    return f"""---
- name: Syntax test for {role_name}
  hosts: localhost
  connection: local
  gather_facts: true
  roles:
  - role: ..
"""


def build_role_files(config: dict[str, Any], role_dir: Path) -> dict[Path, str]:
    role_name = role_dir.name
    description = config["role_descriptions"].get(role_name, f"Manage {role_name} configuration.")
    defaults = load_yaml(role_dir / "defaults" / "main.yml")
    readme = build_role_readme(config, role_name, description, defaults)
    operations = role_dir / "docs" / "operations.md"
    if operations.exists():
        readme = readme.rstrip() + "\n\n" + operations.read_text(encoding="utf-8").strip() + "\n"
    return {
        role_dir / "README.md": readme,
        role_dir / "meta" / "main.yml": build_meta_main(config, role_name, description),
        role_dir / "meta" / "argument_specs.yml": build_argument_specs(role_name, defaults),
        role_dir / "tests" / "test.yml": build_role_test_playbook(config, role_name),
    }


def iter_role_dirs() -> list[Path]:
    return sorted(path for path in ROLES_DIR.iterdir() if path.is_dir())


def write_or_diff(path: Path, content: str, check: bool) -> list[str]:
    normalized = content if content.endswith("\n") else f"{content}\n"
    current = path.read_text(encoding="utf-8") if path.exists() else ""

    if current == normalized:
        return []

    if check:
        return list(
            difflib.unified_diff(
                current.splitlines(),
                normalized.splitlines(),
                fromfile=str(path),
                tofile=f"{path} (generated)",
                lineterm="",
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8")
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate standardized role scaffolding.")
    parser.add_argument("--check", action="store_true", help="Fail if generated files are out of date.")
    args = parser.parse_args()

    config = load_config()
    diffs: list[str] = []

    for role_dir in iter_role_dirs():
        for path, content in build_role_files(config, role_dir).items():
            diffs.extend(write_or_diff(path, content, check=args.check))

    if args.check and diffs:
        print("\n".join(diffs))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
