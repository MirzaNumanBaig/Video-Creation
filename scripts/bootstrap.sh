#!/usr/bin/env bash
# Fetch every submodule at its pinned commit (shallow). Private repos need your git credentials.
set -u
cd "$(dirname "$0")/.."
git submodule update --init --depth 1 || echo "Some submodules failed (private repo / no credentials?). Use: python3 tools/master.py sync <name>"
python3 tools/master.py status
python3 tools/master.py validate
