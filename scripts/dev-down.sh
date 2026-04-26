#!/usr/bin/env bash
# Tear down the local dev environment, including Docker volumes + networks.
#
# Per-service processes (uvicorn, mvn, ng serve) are killed by Ctrl+C inside
# the dev:up `concurrently` foreground process. This script:
#   1. Stops Docker containers
#   2. Removes named volumes (Postgres data, Redis data, Kafka data)
#   3. Removes per-project Docker networks
#
# WARNING: this is a HARD teardown — all local data is wiped.
# For a soft stop that preserves data, run: bash infra/local/docker-all-down.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

bash infra/local/docker-all-down-hard.sh
echo
echo "(Per-service processes were killed by Ctrl+C in dev:up.)"
