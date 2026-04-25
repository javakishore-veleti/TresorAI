#!/usr/bin/env bash
# Install Python deps for the intelligence-service into the project's conda env.
# Uses uv if a pyproject.toml is present; falls back to pip + requirements.txt.

set -euo pipefail

ENV_PATH="$HOME/runtime_data/python_venvs/TresorAI"
SVC_DIR="backend/intelligence-service"

if [[ ! -d "$ENV_PATH" ]]; then
  echo "Conda env not found at $ENV_PATH. Run: npm run setup:conda:create" >&2
  exit 1
fi

PIP="$ENV_PATH/bin/pip"
PY="$ENV_PATH/bin/python"

echo "Upgrading pip + installing uv into $ENV_PATH ..."
"$PIP" install --upgrade pip uv

if [[ -f "$SVC_DIR/pyproject.toml" ]]; then
  echo "Installing $SVC_DIR via uv ..."
  (cd "$SVC_DIR" && "$ENV_PATH/bin/uv" pip install --python "$PY" -e .)
elif [[ -f "$SVC_DIR/requirements.txt" ]]; then
  echo "Installing $SVC_DIR/requirements.txt via pip ..."
  "$PIP" install -r "$SVC_DIR/requirements.txt"
else
  echo "No pyproject.toml or requirements.txt in $SVC_DIR yet — skipping deps install."
  echo "(Service is not scaffolded yet — see plan T06.)"
fi
