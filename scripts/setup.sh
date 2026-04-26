#!/usr/bin/env bash
# First-time setup. Idempotent — safe to re-run; skips work that's already done.
#
# Does NOT download data. Per ADR-0007 + ADR-0012: every dataset load happens
# through the admin portal -> Airflow, never from the CLI.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo
echo "==> Step 1/5: Conda env (\$HOME/runtime_data/python_venvs/TresorAI)"
bash scripts/conda-create.sh

echo
echo "==> Step 2/5: Python deps for intelligence-service (~5-10 min first time)"
bash scripts/python-deps.sh

echo
echo "==> Step 3/5: Root + portal npm deps (in parallel)"
npm install --no-audit --no-fund --silent
bash scripts/install-portals.sh

echo
echo "==> Step 4/5: Brand favicons"
node scripts/generate-favicons.js

echo
echo "==> Step 5/5: Docker infra (Postgres + pgvector · Redis · Kafka)"
bash infra/local/docker-all-up.sh

echo
echo "================================================================="
echo "  Setup complete."
echo
echo "  Daily flow:   npm start"
echo "  Stop:         npm stop"
echo
echo "  Load data:    after 'npm start', open"
echo "                http://localhost:4201/administration/data-management/initial-downloads"
echo "                and click 'Run download' on each dataset."
echo "                (Downloads run via Airflow — not the CLI.)"
echo "================================================================="
