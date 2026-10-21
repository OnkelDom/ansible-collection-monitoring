#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.venv/bin:$PATH"
export ANSIBLE_HOME="$PWD/.ansible"
export ANSIBLE_COLLECTIONS_PATH="$PWD/.ansible/collections"
python tools/generate_role_scaffold.py --check
pytest tests/unit -q
yamllint .
ansible-galaxy collection build --force
artifact="$(python - <<'PYTHON'
import yaml
info = yaml.safe_load(open('galaxy.yml'))
print(f"{info['namespace']}-{info['name']}-{info['version']}.tar.gz")
PYTHON
)"
python tools/check_collection_artifact.py "$artifact"
ansible-galaxy collection install "$artifact" --force --no-deps
if [[ -f tests/run_preflight_checks.py ]]; then python tests/run_preflight_checks.py; fi
bash tests/run_role_syntax_checks.sh
ansible-lint --offline
bash tests/run_collection_sanity.sh "$artifact" "$(python -c "import yaml; print(yaml.safe_load(open('galaxy.yml'))['name'])")"
