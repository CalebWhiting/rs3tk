#!/usr/bin/env bash
# Build and run rs3tk test environments.
#
# Usage:
#   ./scripts/test-quickstart.sh              # lint + typecheck + tests
#   ./scripts/test-quickstart.sh --build      # build the AppImage
#   ./scripts/test-quickstart.sh --shell      # drop into a bash shell
#   ./scripts/test-quickstart.sh --no-cache   # rebuild image from scratch
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

IMAGE="rs3tk-test"
EXTRA_ARGS=()
SHELL_MODE=false
BUILD_MODE=false

for arg in "$@"; do
    case "$arg" in
        --shell)    SHELL_MODE=true ;;
        --build)    BUILD_MODE=true ;;
        --no-cache) EXTRA_ARGS+=("--no-cache") ;;
        *)          echo "Unknown flag: $arg"; exit 1 ;;
    esac
done

if [ "$BUILD_MODE" = true ]; then
    IMAGE="rs3tk-build"
    echo "==> Building AppImage image"
    docker build "${EXTRA_ARGS[@]}" -f "$REPO_ROOT/Dockerfile.build" -t "$IMAGE" "$REPO_ROOT"

    if [ "$SHELL_MODE" = true ]; then
        echo "==> Dropping into shell (source is at /app)"
        exec docker run --rm -it --entrypoint bash "$IMAGE"
    else
        echo "==> Building AppImage (this will take a while)"
        exec docker run --rm "$IMAGE"
    fi
else
    echo "==> Building test image"
    docker build "${EXTRA_ARGS[@]}" -t "$IMAGE" "$REPO_ROOT"

    if [ "$SHELL_MODE" = true ]; then
        echo "==> Dropping into shell (source is at /app)"
        exec docker run --rm -it --entrypoint bash "$IMAGE"
    else
        echo "==> Running verification (lint + typecheck + tests)"
        exec docker run --rm "$IMAGE"
    fi
fi
