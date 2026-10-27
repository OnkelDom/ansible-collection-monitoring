export PATH := $(CURDIR)/.venv/bin:$(PATH)
export ANSIBLE_HOME := $(CURDIR)/.ansible
export ANSIBLE_COLLECTIONS_PATH := $(CURDIR)/.ansible/collections
PYTHON ?= python3

.PHONY: prepare lint syntax unit test ci build package-smoke

prepare:
	$(PYTHON) -m pip install -r requirements-test.txt
	ansible-galaxy collection install -r requirements.yml
	@if [ -f requirements-dev.yml ]; then ansible-galaxy collection install -r requirements-dev.yml; fi

lint:
	$(PYTHON) tools/check_repository.py
	$(PYTHON) tools/generate_role_scaffold.py --check
	yamllint .
	ansible-lint --offline

syntax:
	bash tests/run_role_syntax_checks.sh

unit:
	$(PYTHON) -m pytest tests/unit -q

test ci:
	bash tests/run_checks.sh

build:
	ansible-galaxy collection build --force

package-smoke: build
	$(PYTHON) tools/check_collection_artifact.py "$$($(PYTHON) tools/collection_metadata.py artifact)"
	$(PYTHON) tools/check_monitoring_artifact.py "$$($(PYTHON) tools/collection_metadata.py artifact)"
