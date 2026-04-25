# Source me; do NOT execute.
# Activates the TrésorAI conda env in the current shell.
#
# Usage: source ./scripts/conda-activate.sh

ENV_PATH="$HOME/runtime_data/python_venvs/TresorAI"

if [[ ! -d "$ENV_PATH" ]]; then
  echo "Conda env not found at: $ENV_PATH" >&2
  echo "Run: npm run setup:conda:create" >&2
  return 1 2>/dev/null || exit 1
fi

# Make sure `conda activate` is wired into this shell.
if ! type conda 2>/dev/null | grep -q 'function'; then
  CONDA_BASE="$(conda info --base 2>/dev/null || true)"
  if [[ -n "${CONDA_BASE}" && -f "${CONDA_BASE}/etc/profile.d/conda.sh" ]]; then
    # shellcheck disable=SC1091
    source "${CONDA_BASE}/etc/profile.d/conda.sh"
  fi
fi

conda activate "$ENV_PATH"
echo "Activated: $ENV_PATH"
