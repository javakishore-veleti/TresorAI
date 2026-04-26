#!/usr/bin/env bash
# Hard teardown — stops containers AND removes named volumes + per-project networks.
# WARNING: destroys all local data (Postgres rows, Kafka topics & messages, Redis cache).
# For a soft stop that preserves data, use ./docker-all-down.sh instead.

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
    echo "==> Stopping + wiping: $stack"
    (cd "$stack" && docker compose down --volumes --remove-orphans)
  fi
done

echo
echo "Hard teardown complete — containers, volumes, and per-project networks removed."
echo "All local data has been wiped."
