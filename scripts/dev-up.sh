#!/usr/bin/env bash
# Bring up the full local TrésorAI dev environment in one command:
#   0. Sync npm deps (root + each portal) — picks up package.json changes from teammates
#   1. Docker infra stacks (postgres+pgvector, redis, kafka)
#   2. Every backend service that has been scaffolded
#   3. Both portals if they have been scaffolded
#
# Services and portals that are not yet scaffolded are skipped silently.
# All running processes are multiplexed in a single terminal via `concurrently`,
# with colour-coded prefixes per service. Ctrl+C kills all of them.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

CONDA_ENV="$HOME/runtime_data/python_venvs/TresorAI"

# ---------- Pre-flight: setup must have been run ----------
if [[ ! -d "$CONDA_ENV" ]]; then
  echo
  echo "Conda env not found at $CONDA_ENV"
  echo "First-time on this laptop?  Run:   npm run setup"
  echo
  exit 1
fi

# ---------- Step 0: keep npm deps in sync ----------
# Runs in every dev:up so package.json changes from other teammates are picked up
# without anyone needing to remember `npm install`. Fast (~5s) when nothing changed.
echo "==> Step 0: Sync npm deps"

if [[ -f package.json ]]; then
  echo "  - root"
  npm install --no-audit --no-fund --silent
fi

for portal in frontend/portal-customer frontend/portal-admin; do
  if [[ -f "$portal/package.json" ]]; then
    echo "  - $portal"
    (cd "$portal" && npm install --no-audit --no-fund --silent)
  fi
done

# ---------- Step 1: verify Docker is up (we no longer start it here) ----------
echo
echo "==> Step 1: Docker infra check"
if ! docker ps --filter "name=tresorai-postgres" --filter "status=running" --format '{{.Names}}' | grep -q tresorai-postgres; then
  echo
  echo "Docker stacks not running."
  echo "Bring them up first:    npm run start-docker"
  echo "Or to start everything: npm run start-docker && npm start"
  echo
  exit 1
fi
echo "  Docker stacks running."

# ---------- Step 2 + 3: assemble service commands ----------
COMMANDS=()
NAMES=()
COLORS=()

# intelligence-service (Python / FastAPI)
if [[ -f backend/intelligence-service/pyproject.toml || -f backend/intelligence-service/requirements.txt ]]; then
  if [[ -x "$CONDA_ENV/bin/uvicorn" ]]; then
    COMMANDS+=("cd backend/intelligence-service && \"$CONDA_ENV/bin/uvicorn\" app.main:app --reload --port 8090")
    NAMES+=("intel")
    COLORS+=("yellow")
  else
    echo "    (skipping intelligence-service: uvicorn not found at $CONDA_ENV/bin/uvicorn — run 'npm run setup')"
  fi
fi

# admin-api (Python / FastAPI) — dedicated admin operations service
if [[ -f backend/admin-api/pyproject.toml ]]; then
  if [[ -x "$CONDA_ENV/bin/uvicorn" ]]; then
    COMMANDS+=("cd backend/admin-api && \"$CONDA_ENV/bin/uvicorn\" app.main:app --reload --port 8091")
    NAMES+=("admin-api")
    COLORS+=("white")
  else
    echo "    (skipping admin-api: uvicorn not found at $CONDA_ENV/bin/uvicorn — run 'npm run setup')"
  fi
fi

# api-gateway (Java / Spring Boot)
if [[ -f backend/api-gateway/pom.xml ]]; then
  COMMANDS+=("cd backend/api-gateway && mvn spring-boot:run")
  NAMES+=("api-gw")
  COLORS+=("cyan")
fi

# ingest-service (Java / Spring Boot)
if [[ -f backend/ingest-service/pom.xml ]]; then
  COMMANDS+=("cd backend/ingest-service && mvn spring-boot:run")
  NAMES+=("ingest")
  COLORS+=("magenta")
fi

# portal-customer (Angular) — node_modules guaranteed by Step 0 if package.json exists
if [[ -f frontend/portal-customer/package.json ]]; then
  COMMANDS+=("cd frontend/portal-customer && npm run start")
  NAMES+=("customer")
  COLORS+=("green")
fi

# portal-admin (Angular) — node_modules guaranteed by Step 0 if package.json exists
if [[ -f frontend/portal-admin/package.json ]]; then
  COMMANDS+=("cd frontend/portal-admin && npm run start")
  NAMES+=("admin")
  COLORS+=("blue")
fi

# ---------- Step 4: run them all in parallel ----------
if [[ ${#COMMANDS[@]} -eq 0 ]]; then
  echo
  echo "==> Step 2-3: nothing to start yet"
  echo
  echo "    Docker infra is up, but no backend services or portals have been scaffolded."
  echo "    Land T02 / T04 / T05 / T06 to enable parallel start here."
  echo
  echo "    Health checks you CAN run today:"
  echo "      docker exec -it tresorai-redis    redis-cli ping"
  echo "      psql postgresql://tresorai:tresorai@localhost:5432/tresorai -c 'SELECT extname FROM pg_extension;'"
  exit 0
fi

NAMES_JOINED=$(IFS=,; echo "${NAMES[*]}")
COLORS_JOINED=$(IFS=,; echo "${COLORS[*]}")

echo
echo "==> Step 2-3: starting [${NAMES[*]}] in parallel"
echo "    (Ctrl+C kills all of them; run 'npm stop' afterwards to stop Docker.)"
echo

exec npx concurrently \
  --names "$NAMES_JOINED" \
  --prefix-colors "$COLORS_JOINED" \
  --kill-others-on-fail \
  --handle-input \
  "${COMMANDS[@]}"
