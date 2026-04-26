#!/usr/bin/env bash
# Install npm deps for both portals in parallel.
# Run this once after first clone — or any time package.json changes.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Installing npm deps for both portals (in parallel)..."
exec npx concurrently \
  --names "customer,admin" \
  --prefix-colors "green,blue" \
  "cd frontend/portal-customer && npm install --no-audit --no-fund" \
  "cd frontend/portal-admin    && npm install --no-audit --no-fund"
