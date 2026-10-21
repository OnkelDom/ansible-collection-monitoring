#!/usr/bin/env bash
set -euo pipefail
ARTIFACT="${1:?collection artifact required}"
COLLECTION="${2:?collection name required}"
[[ "$COLLECTION" =~ ^[a-z][a-z0-9_]*$ ]] || exit 2
SANITY_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/degit-sanity.XXXXXX")"
trap 'rm -rf "$SANITY_ROOT"' EXIT
COLLECTION_PATH="$SANITY_ROOT/ansible_collections/degit/$COLLECTION"
mkdir -p "$COLLECTION_PATH"
tar -xzf "$ARTIFACT" -C "$COLLECTION_PATH"
# Run outside the checkout: git ignores .ansible/, which would otherwise make
# ansible-test skip every target in an installed collection under that directory.
cd "$COLLECTION_PATH"
ansible-test sanity --test compile --test import --python 3.12 --requirements
