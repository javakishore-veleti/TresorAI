#!/usr/bin/env bash
# Remove the TrésorAI conda env. Prompts for confirmation.

set -euo pipefail

ENV_PATH="$HOME/runtime_data/python_venvs/TresorAI"

if [[ ! -d "$ENV_PATH" ]]; then
  echo "No conda env at $ENV_PATH — nothing to remove."
  exit 0
fi

read -p "Remove conda env at $ENV_PATH? [y/N] " ans
case "${ans:-n}" in
  y|Y|yes|YES) ;;
  *) echo "Aborted."; exit 0 ;;
esac

conda env remove --prefix "$ENV_PATH" -y
echo "Removed."
