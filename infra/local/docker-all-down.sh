#!/usr/bin/env bash
# Stop every TrésorAI local infra stack (reverse of docker-all-up.sh order).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Reverse of up order so dependents stop before their dependencies.
# Keep this in sync with docker-all-up.sh STACKS.
STACKS=(
  # mlflow
  # qdrant
  airflow
  kafka
  redis
  postgres
)

for stack in "${STACKS[@]}"; do
  if [[ -f "$stack/docker-compose.yaml" ]]; then
    echo "==> Stopping: $stack"
    (cd "$stack" && docker compose down)
  fi
done

echo
echo "All TrésorAI local stacks stopped."
