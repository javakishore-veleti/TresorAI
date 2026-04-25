# ADR-0009: Conda env at a pinned project path

- Status: Accepted
- Date: 2026-04-25

## Context
The intelligence-service is Python 3.12. We want a single, reproducible Python environment that any contributor — or a fresh laptop — sets up the same way. Three options were on the table: (a) repo-local `.venv`, (b) named conda env (`conda create -n tresorai`), (c) prefix-pinned conda env at a known absolute path.

## Decision
A prefix-pinned conda env at `$HOME/runtime_data/python_venvs/TresorAI`. Created via `npm run setup:conda:create` (which wraps `conda create --prefix ...`). Activated by sourcing `./scripts/conda-activate.sh`.

## Consequences
- (+) Same path on every contributor's laptop — IDE configs, debugger paths, and shell aliases are portable.
- (+) Outside the repo tree — not checked in by accident, not blown away by `git clean -fdx`.
- (+) Project name (`TresorAI`) is the env directory name — visible in `ls $HOME/runtime_data/python_venvs/`, which is helpful when juggling multiple projects.
- (−) Requires conda installed (Miniconda or Anaconda); a `pip + venv` user would need to run a different setup path.
- (−) Hard-coded `$HOME` path means CI / Docker images use a different setup mechanism (uv + Docker layer cache).
