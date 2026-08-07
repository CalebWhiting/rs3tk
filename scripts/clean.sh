#!/usr/bin/env bash
# Remove all build artifacts, caches, and generated files.
#
# Usage (from the monorepo root):
#   bash scripts/clean.sh [--deep]
#
# Options:
#   --deep    Also remove node_modules/ (requires pnpm install to restore)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Cleaning build artifacts"
rm -rf "$ROOT/.build"
rm -rf "$ROOT/squashfs-root"

# PyInstaller bridge binary
if [[ -f "$ROOT/packages/electron/resources/rs3tk-bridge" ]]; then
    rm -f "$ROOT/packages/electron/resources/rs3tk-bridge"
    echo "    removed packages/electron/resources/rs3tk-bridge"
fi

# Python egg-info dirs (scattered by pip install -e)
find "$ROOT" -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true

if [[ "${1:-}" == "--deep" ]]; then
    echo "==> Deep clean: removing node_modules"
    rm -rf "$ROOT/node_modules"
    rm -rf "$ROOT/packages/electron/node_modules"
    echo "    Run 'pnpm install' to restore"
fi

echo "==> Done"
