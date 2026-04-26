#!/usr/bin/env bash
# Install Python deps for ALL Python services into the project's conda env.
# Today: intelligence-service + admin-api. Adds new services as they appear.
# Idempotent: uv pip install is fast when nothing changed.

set -euo pipefail

ENV_PATH="$HOME/runtime_data/python_venvs/TresorAI"

if [[ ! -d "$ENV_PATH" ]]; then
  echo "Conda env not found at $ENV_PATH. Run: npm run setup" >&2
  exit 1
fi

PIP="$ENV_PATH/bin/pip"
PY="$ENV_PATH/bin/python"

echo "Upgrading pip + installing uv into $ENV_PATH ..."
"$PIP" install --upgrade pip uv --quiet

# Each Python service that has pyproject.toml gets installed editable into the env
for svc in backend/intelligence-service backend/admin-api; do
  if [[ -f "$svc/pyproject.toml" ]]; then
    echo "Installing $svc deps via uv ..."
    (cd "$svc" && "$ENV_PATH/bin/uv" pip install --python "$PY" -e .)
  elif [[ -f "$svc/requirements.txt" ]]; then
    echo "Installing $svc/requirements.txt via pip ..."
    "$PIP" install -r "$svc/requirements.txt"
  else
    echo "  (skipping $svc — not scaffolded yet)"
  fi
done

echo "Python deps in sync."
