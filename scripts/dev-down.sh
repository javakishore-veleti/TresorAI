#!/usr/bin/env bash
# Stop TrésorAI app processes only — Docker stacks are LEFT RUNNING.
#
# Most of the time you'll just Ctrl+C in the foreground 'npm start' terminal.
# This script is for cleaning up orphaned uvicorn / ng serve / mvn processes
# that survived a crash or a forced-quit terminal.
#
# For Docker control, run separately:
#   npm run stop-docker        soft stop, volumes preserved
#   npm run stop-docker-hard   hard teardown, volumes + networks wiped

set -euo pipefail

APP_PORTS=(
  4200    # portal-customer
  4201    # portal-admin
  8080    # api-gateway
  8081    # ingest-service
  8090    # intelligence-service
  8091    # admin-api
)

echo "==> Stopping TrésorAI app processes (best effort)"
killed_any=0
for port in "${APP_PORTS[@]}"; do
  pids="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "  - port $port -> kill $pids"
    echo "$pids" | xargs kill 2>/dev/null || true
    killed_any=1
  fi
done

if [[ $killed_any -eq 0 ]]; then
  echo "  (no app processes were running on any TrésorAI port)"
fi

echo
echo "Docker stacks are still running."
echo "  npm run stop-docker        — soft stop, data preserved"
echo "  npm run stop-docker-hard   — hard teardown, all local data wiped"
