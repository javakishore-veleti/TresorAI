# Source me; do NOT execute.
# Deactivates whatever conda env is currently active in this shell.
#
# Usage: source ./scripts/conda-deactivate.sh

if command -v conda >/dev/null 2>&1; then
  conda deactivate
  echo "Deactivated."
else
  echo "conda not on PATH — nothing to deactivate." >&2
fi
