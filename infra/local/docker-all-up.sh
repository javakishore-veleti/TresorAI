#!/usr/bin/env bash
# Bring up every TrésorAI local infra stack in dependency order.
#
# Each subdirectory under infra/local/ that contains a docker-compose.yaml is
# treated as an independent stack. Add a new stack by creating <name>/docker-compose.yaml
# and adding <name> to the STACKS array below in the right order.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Order: data stores first, then ML services that may depend on them.
# Starting slim — only the core stacks from the locked plan are active.
# Uncomment additional stacks as we expand scope.
STACKS=(
  postgres
  redis
  kafka
  airflow    # ADR-0012 — orchestrator for all 3 AI/ML tracks + Initial Downloads
  # qdrant   # alternate vector DB — pgvector is primary per ADR-003; enable for experimentation
  # mlflow   # XGBoost experiment tracking — enable for M5
)

for stack in "${STACKS[@]}"; do
  if [[ -f "$stack/docker-compose.yaml" ]]; then
    echo "==> Bringing up: $stack"
    (cd "$stack" && docker compose up -d)
  else
    echo "--- Skipping $stack (no docker-compose.yaml)"
  fi
done

echo
echo "All TrésorAI local stacks started. Run ./docker-all-status.sh to verify."
