#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
node --test services/embed-session/test/*.test.mjs web/*.test.mjs
PYTHONPATH=services/provisioning python3 -m unittest discover -s services/provisioning/tests -v
python3 -m compileall -q services/provisioning
python3 scripts/check_publication.py
