#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.venv/bin:$PATH"
export ANSIBLE_HOME="$PWD/.ansible"
export ANSIBLE_COLLECTIONS_PATH="$PWD/.ansible/collections"
python tools/check_repository.py
python tools/generate_role_scaffold.py --check
python tools/build_exporters.py --check
pytest tests/unit -q
yamllint .
ansible-galaxy collection build --force
artifact=$(python tools/collection_metadata.py artifact)
python tools/check_collection_artifact.py "$artifact"
python tools/check_monitoring_artifact.py "$artifact"
ansible-galaxy collection install "$artifact" --force --no-deps
python tests/run_preflight_checks.py
bash tests/run_role_syntax_checks.sh
ansible-lint --offline
bash tests/run_collection_sanity.sh "$artifact"
monitoring_tools=${MONITORING_TEST_TOOLS_DIR:-"$PWD/.ansible/monitoring-tools"}
python tests/install_monitoring_test_tools.py --dest "$monitoring_tools"
python tests/run_lpm_checks.py --promtool "$monitoring_tools/promtool" --amtool "$monitoring_tools/amtool"
python tests/run_lpm_inhibition_checks.py --alertmanager "$monitoring_tools/alertmanager"
PROMTOOL="$monitoring_tools/promtool" python tests/run_proxmox_checks.py
