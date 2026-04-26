#!/usr/bin/env bash
# Tear down the local dev environment.
#
# Per-service processes (uvicorn, mvn, ng serve) are killed by Ctrl+C inside
# the dev:up `concurrently` foreground process. This script just stops the
# Docker stacks. Run it after you have stopped the foreground services.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

npm run infra:down
echo
echo "Docker stacks stopped. (Per-service processes were killed by Ctrl+C in dev:up.)"
