#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import io
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml
from ruamel.yaml import YAML
try:
    from tools.format_yaml import quote_ambiguous_strings
except ModuleNotFoundError:
    from format_yaml import quote_ambiguous_strings


ROOT = Path(__file__).resolve().parents[1]
ROLES_DIR = ROOT / "roles"
CONFIG_PATH = ROOT / "tools" / "role_scaffold_config.yml"
JINJA_EXPRESSION_RE = re.compile(r"^\s*\{\{\s*(.+?)\s*\}\}\s*$")


def yaml_dump(data: Any) -> str:
    formatter = YAML()
    formatter.explicit_start = True
    formatter.default_flow_style = False
    formatter.allow_unicode = False
    formatter.sort_base_mapping_type_on_output = False
    formatter.indent(mapping=2, sequence=2, offset=0)
    formatter.width = 1000

    buffer = io.StringIO()
    formatter.dump(quote_ambiguous_strings(deepcopy(data)), buffer)
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


def resolve_templated_default(value: Any, defaults: dict[str, Any], seen: set[str] | None = None) -> Any:
    if not isinstance(value, str):
        return value

    match = JINJA_EXPRESSION_RE.match(value)
    if not match:
        return value

    expression = match.group(1).strip()
    parts = [part.strip() for part in expression.split("|")]
    if not parts:
        return value

    variable_name = parts[0]
    filters = parts[1:]

    if "bool" in filters:
        return False
    if "int" in filters:
        return 0

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", variable_name):
        return value

    resolved_seen = seen or set()
    if variable_name in resolved_seen or variable_name not in defaults:
        return value

    return resolve_templated_default(defaults[variable_name], defaults, resolved_seen | {variable_name})


def infer_type_from_defaults(value: Any, defaults: dict[str, Any]) -> str:
    return infer_type(resolve_templated_default(value, defaults))


def infer_elements_from_defaults(value: Any, defaults: dict[str, Any]) -> str | None:
    return infer_elements(resolve_templated_default(value, defaults))


def get_platforms(config: dict[str, Any], role_name: str) -> list[dict[str, Any]]:
    return deepcopy(config.get("role_platform_overrides", {}).get(role_name, config["common_platforms"]))


def get_galaxy_tags(config: dict[str, Any], role_name: str) -> list[str]:
    tags = ["linux", "system", "infrastructure"]
    role_tags = config.get("role_galaxy_tags", {}).get(role_name, [])
    return list(dict.fromkeys(tags + role_tags))


def get_role_dependencies(config: dict[str, Any], role_name: str) -> list[Any]:
    return deepcopy(config.get("role_dependencies", {}).get(role_name, []))


def get_example_playbook(config: dict[str, Any], role_name: str) -> str:
    examples = config.get("role_example_playbooks", {})
    if role_name in examples:
        return examples[role_name].rstrip()

    collection = f"{config['collection_namespace']}.{config['collection_name']}"
    return f"""- name: Apply {role_name}
  hosts: all
  become: true
  gather_facts: true
  roles:
    - role: {collection}.{role_name}"""


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
            "license": config.get("role_licenses", {}).get(role_name, "MIT"),
            "min_ansible_version": config["min_ansible_version"],
            "platforms": [
                {
                    "name": platform["name"],
                    "versions": [str(version) for version in platform["versions"]],
                }
                for platform in platforms
            ],
            "galaxy_tags": get_galaxy_tags(config, role_name),
        },
        "dependencies": get_role_dependencies(config, role_name),
    }
    return yaml_dump(data)


def build_argument_specs(role_name: str, defaults: Any, config: dict[str, Any] | None = None) -> str:
    options: dict[str, Any] = {}
    if isinstance(defaults, dict):
        for variable_name, value in defaults.items():
            entry: dict[str, Any] = {
                "description": [f"Controls `{variable_name}` for the `{role_name}` role."],
                "required": False,
                "type": infer_type_from_defaults(value, defaults),
            }
            elements = infer_elements_from_defaults(value, defaults)
            if elements:
                entry["elements"] = elements
            if variable_name.endswith(("_password", "_passphrase", "_token", "_secret", "_api_key", "_user_key", "_private_key")) or variable_name in {"msmtp_accounts", "k3s_platform_apps_runtime_env"}:
                entry["no_log"] = True
            overrides = (config or {}).get("role_argument_overrides", {}).get(role_name, {})
            entry.update(overrides.get(variable_name, {}))
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
    platforms = get_platforms(config, role_name)
    defaults_block = render_defaults_block(defaults)
    example_playbook = get_example_playbook(config, role_name)
    return f"""# {role_name}

{description}

## Supported platforms

{format_platform_list(platforms)}

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

{config.get('role_notes', {}).get(role_name, 'Run this role only on hosts assigned to its responsibility. Review the defaults and required inputs before rollout.')}

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

{defaults_block}
## Example Playbook

```yaml
{example_playbook}
```

## Testing

Build and install the current collection checkout before running syntax checks, so the
fully qualified role reference resolves to this implementation.

Run `python tools/generate_role_scaffold.py --check`, `pytest tests/unit` and
`bash tests/run_role_syntax_checks.sh` from the collection root.
CI additionally runs YAML lint, Ansible lint, collection build/install and container smoke tests.
VM functional results are tracked separately; metadata lists intended compatibility,
not proof that every feature has passed on every distribution.

## Dependencies

Install the collection dependencies from `requirements.yml`. Role dependencies:
`{get_role_dependencies(config, role_name)}`.

## Change management

Use check mode where the underlying modules support it. Review the diff before applying
changes. Network, firewall, identity and storage changes need an out-of-band recovery
path. Secrets belong in Ansible Vault or the operator secret store, never in defaults.
"""


def build_role_test_playbook(config: dict[str, Any], role_name: str) -> str:
    return f"""---
- name: Syntax test for {role_name}
  hosts: localhost
  connection: local
  gather_facts: true
  roles:
  - role: {config["collection_namespace"]}.{config["collection_name"]}.{role_name}
"""


def build_preflight(config: dict[str, Any], role_name: str) -> str:
    names = {item["name"] for item in get_platforms(config, role_name)}
    conditions = []
    if "Debian" in names:
        conditions.append("(ansible_facts['distribution'] == 'Debian' and ansible_facts['distribution_major_version'] == '13')")
    if "Ubuntu" in names:
        conditions.append("(ansible_facts['distribution'] == 'Ubuntu' and ansible_facts['distribution_version'] in ['22.04', '24.04', '26.04'])")
    if "EL" in names:
        conditions.append("(ansible_facts['distribution'] in ['Rocky', 'RedHat'] and ansible_facts['distribution_major_version'] == '9')")
    if "Windows" in names:
        conditions.append("ansible_facts['os_family'] == 'Windows'")
    required = {"distribution", "distribution_version", "distribution_major_version", "os_family", "architecture"}
    for path in (ROLES_DIR / role_name).rglob("*"):
        if path.is_file() and path.suffix in {".yml", ".j2"} and path.name != "preflight.yml":
            required.update(re.findall(r"ansible_facts\.([A-Za-z_][A-Za-z_0-9]*)", path.read_text(encoding="utf-8")))
            required.update(re.findall(r'ansible_facts\[[\'"]([A-Za-z_][A-Za-z_0-9]*)[\'"]\]', path.read_text(encoding="utf-8")))
    if required.intersection({"default_ipv4", "default_ipv6"}):
        required.difference_update({"default_ipv4", "default_ipv6"})
        required.add("interfaces")
    required.discard("services")  # Service facts have their own explicit task where needed.
    required.difference_update({"get", "keys", "items", "values"})  # Mapping methods are not facts.
    condition = str(sorted(required)) + " | difference(ansible_facts.keys()) | length > 0"
    tasks = [
        {"name": "Collect missing Linux platform facts", "ansible.builtin.setup": {},
         "when": [condition, "ansible_connection | default('ssh') not in ['winrm', 'psrp']", "ansible_facts.get('os_family', '') != 'Windows'"]},
        *([{"name": "Collect missing Windows platform facts", "ansible.windows.setup": {},
            "when": ["['os_family', 'architecture', 'distribution', 'distribution_version'] | difference(ansible_facts.keys()) | length > 0", "ansible_connection | default('ssh') in ['winrm', 'psrp'] or ansible_facts.get('os_family', '') == 'Windows'"]}] if "Windows" in names else []),
        {"name": "Validate the supported operating system release", "ansible.builtin.assert": {
            "that": [" or ".join(conditions) or "false"],
            "fail_msg": f"Unsupported or unimplemented role/platform combination for {role_name}. See the role README.",
            "quiet": True}},
        {"name": "Load family platform variables", "ansible.builtin.include_vars": {
            "file": "{{ role_path }}/vars/platform/{{ ansible_facts['os_family'] }}.yml"}},
        {"name": "Load distribution platform variables", "ansible.builtin.include_vars": {
            "file": "{{ role_path }}/vars/platform/{{ ansible_facts['distribution'] }}.yml"},
            "when": "ansible_facts['os_family'] != 'Windows' and ansible_facts['distribution'] != ansible_facts['os_family']"},
        {"name": "Load release platform variables", "ansible.builtin.include_vars": "{{ item }}",
         "with_first_found": [{"files": ["{{ ansible_facts['distribution'] }}-{{ ansible_facts['distribution_version'] }}.yml", "{{ ansible_facts['distribution'] }}-{{ ansible_facts['distribution_major_version'] }}.yml"],
                               "paths": ["{{ role_path }}/vars/platform"], "skip": True}]},
    ]
    return yaml_dump(tasks)


def build_role_files(config: dict[str, Any], role_dir: Path) -> dict[Path, str]:
    role_name = role_dir.name
    description = config["role_descriptions"].get(role_name, f"Manage {role_name} configuration.")
    defaults = load_yaml(role_dir / "defaults" / "main.yml")
    readme = build_role_readme(config, role_name, description, defaults)
    operations = role_dir / "docs" / "operations.md"
    if operations.exists():
        readme = readme.rstrip() + "\n\n" + operations.read_text(encoding="utf-8").strip() + "\n"
    files = {
        role_dir / "tasks" / "main.yml": yaml_dump([
            {"name": "Prepare facts and platform variables", "ansible.builtin.import_tasks": "preflight.yml", "tags": "always"},
            {"name": "Apply " + role_name + " configuration", "ansible.builtin.import_tasks": "configuration.yml", "tags": role_name},
        ]),
        role_dir / "tasks" / "preflight.yml": build_preflight(config, role_name),
        role_dir / "README.md": readme,
        role_dir / "meta" / "main.yml": build_meta_main(config, role_name, description),
        role_dir / "meta" / "argument_specs.yml": build_argument_specs(role_name, defaults, config),
        role_dir / "tests" / "test.yml": build_role_test_playbook(config, role_name),
    }
    for relative, initial in (("defaults/main.yml", {}), ("tasks/configuration.yml", [])):
        path = role_dir / relative
        if not path.exists():
            files[path] = yaml_dump(initial)
    for family in ("Debian", "RedHat", "Ubuntu", "Rocky"):
        path = role_dir / "vars" / "platform" / (family + ".yml")
        if not path.exists():
            files[path] = yaml_dump({})
    for distro, version in (("Debian", "13"), ("Ubuntu", "22.04"), ("Ubuntu", "24.04"), ("Ubuntu", "26.04"), ("Rocky", "9"), ("RedHat", "9")):
        path = role_dir / "vars" / "platform" / f"{distro}-{version}.yml"
        if not path.exists():
            files[path] = yaml_dump({})
    return files


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
