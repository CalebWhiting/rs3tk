#!/usr/bin/env bash
# Build the rs3tk-backend binary using PyInstaller.
#
# Usage (from the repo root):
#   electron/scripts/build-backend.sh
#
# Output:
#   electron/resources/rs3tk-backend  (single-file Linux binary)
#
# Requirements:
#   - Python 3.11+ on PATH
#   - Network access (for pip install)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ELECTRON_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$ELECTRON_DIR/build/backend"
VENV_DIR="$BUILD_DIR/venv"
OUTPUT="$ELECTRON_DIR/resources/rs3tk-backend"

echo "==> Building rs3tk-backend"
echo "    Project root: $PROJECT_ROOT"
echo "    Build dir:    $BUILD_DIR"
echo "    Output:       $OUTPUT"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR" "$ELECTRON_DIR/resources"

# Create a fresh venv
echo "==> Creating build venv"
python3 -m venv "$VENV_DIR"

# Install rs3tk and PyInstaller into the venv
echo "==> Installing rs3tk + PyInstaller"
"$VENV_DIR/bin/pip" install -q --upgrade pip
"$VENV_DIR/bin/pip" install -q "$PROJECT_ROOT"
"$VENV_DIR/bin/pip" install -q pyinstaller

# Run PyInstaller
echo "==> Running PyInstaller"
"$VENV_DIR/bin/python" -m PyInstaller \
    --clean \
    --distpath "$BUILD_DIR/dist" \
    --workpath "$BUILD_DIR/build" \
    --specpath "$BUILD_DIR" \
    "$ELECTRON_DIR/rs3tk-backend.spec"

# Copy to resources/
cp "$BUILD_DIR/dist/rs3tk-backend" "$OUTPUT"
chmod 755 "$OUTPUT"

# Report size
SIZE=$(du -h "$OUTPUT" | cut -f1)
echo "==> Done: $OUTPUT ($SIZE)"

# Clean up build artifacts (keep the binary)
rm -rf "$BUILD_DIR/build" "$BUILD_DIR/dist" "$VENV_DIR"
