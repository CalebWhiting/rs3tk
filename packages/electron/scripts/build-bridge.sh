#!/usr/bin/env bash
# Build the rs3tk-bridge binary using PyInstaller.
#
# Usage (from the monorepo root):
#   bash packages/electron/scripts/build-bridge.sh
#
# Output:
#   packages/electron/resources/rs3tk-bridge  (single-file Linux binary)
#
# Requirements:
#   - Python 3.11+ on PATH
#   - uv on PATH
#   - Network access (for pip install)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ELECTRON_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MONOREPO_ROOT="$(cd "$ELECTRON_DIR/../.." && pwd)"
BUILD_DIR="$ELECTRON_DIR/build/bridge"
VENV_DIR="$BUILD_DIR/venv"
OUTPUT="$ELECTRON_DIR/resources/rs3tk-bridge"

echo "==> Building rs3tk-bridge"
echo "    Monorepo root: $MONOREPO_ROOT"
echo "    Build dir:     $BUILD_DIR"
echo "    Output:        $OUTPUT"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR" "$ELECTRON_DIR/resources"

echo "==> Creating build venv"
uv venv "$VENV_DIR"

echo "==> Installing rs3tk-core + PyInstaller"
uv pip install --python "$VENV_DIR/bin/python" -q "$MONOREPO_ROOT/packages/core"
uv pip install --python "$VENV_DIR/bin/python" -q pyinstaller

# PyInstaller's analysis needs the bridge module to be importable from
# the venv. We make it a package by copying the file in as __init__.py.
mkdir -p "$VENV_DIR/lib/rs3tk_bridge"
cp "$ELECTRON_DIR/src/bridge/rs3tk_bridge.py" "$VENV_DIR/lib/rs3tk_bridge/__init__.py"

echo "==> Running PyInstaller"
# Pass the venv lib path (where rs3tk_bridge/ now lives) to PyInstaller
# via env var so the spec can locate it without relying on __file__.
RS3TK_BRIDGE_VENV_LIB="$VENV_DIR/lib" \
"$VENV_DIR/bin/python" -m PyInstaller \
    --clean \
    --distpath "$BUILD_DIR/dist" \
    --workpath "$BUILD_DIR/build" \
    "$ELECTRON_DIR/rs3tk-bridge.spec"

cp "$BUILD_DIR/dist/rs3tk-bridge" "$OUTPUT"
chmod 755 "$OUTPUT"

SIZE=$(du -h "$OUTPUT" | cut -f1)
echo "==> Done: $OUTPUT ($SIZE)"

rm -rf "$BUILD_DIR"
