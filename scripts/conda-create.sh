#!/usr/bin/env bash
# Create the TrésorAI conda env at the pinned project path.
# Idempotent: re-running is a no-op once the env exists.

set -euo pipefail

ENV_PATH="$HOME/runtime_data/python_venvs/TresorAI"
PYTHON_VERSION="3.12"

if ! command -v conda >/dev/null 2>&1; then
  echo "Error: conda not found on PATH. Install Miniconda or Anaconda first." >&2
  exit 1
fi

mkdir -p "$(dirname "$ENV_PATH")"

if [[ -d "$ENV_PATH" ]]; then
  echo "Conda env already exists at: $ENV_PATH"
  echo "To recreate it, run: npm run setup:conda:remove && npm run setup:conda:create"
  exit 0
fi

echo "Creating conda env at: $ENV_PATH (python=$PYTHON_VERSION)"
conda create -y --prefix "$ENV_PATH" "python=$PYTHON_VERSION"

echo
echo "Conda env created."
echo "Activate with:   source ./scripts/conda-activate.sh"
echo "Deactivate with: source ./scripts/conda-deactivate.sh"
