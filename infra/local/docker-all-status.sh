#!/usr/bin/env bash
# Show docker compose ps for every active TrésorAI local infra stack.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Keep this in sync with docker-all-up.sh STACKS.
STACKS=(
  postgres
  redis
  kafka
  # qdrant
  # mlflow
)

for stack in "${STACKS[@]}"; do
  echo "---- $stack ----"
  if [[ -f "$stack/docker-compose.yaml" ]]; then
    (cd "$stack" && docker compose ps)
  else
    echo "  (no docker-compose.yaml)"
  fi
  echo
done
