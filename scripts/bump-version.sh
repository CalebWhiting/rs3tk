#!/usr/bin/env bash
# Bump the version across all packages in the monorepo.
#
# Usage:
#   ./scripts/bump-version.sh 1.2.3
#
# Updates version in:
#   - package.json (root)
#   - packages/core/pyproject.toml
#   - packages/core/src/rs3tk_core/__init__.py
#   - packages/cli/pyproject.toml
#   - packages/electron/package.json
#   - packages/electron/pyproject.toml
#   - packages/electron/requirements.txt
#   - packaging/rpm/rs3tk.spec
#   - packaging/rpm/rs3tk-electron.spec
#   - packaging/alpine/APKBUILD
#   - packaging/arch/PKGBUILD
#   - packaging/arch/python-rs3tk/PKGBUILD
#   - packaging/deb/debian/changelog
#
# Note: scripts/ derive VERSION dynamically from pyproject.toml.
# Note: packaging/deb/debian/changelog preserves the Debian revision (-N).
#
# Then regenerates lockfiles.
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <version>" >&2
    echo "Example: $0 1.2.3" >&2
    exit 1
fi

VERSION="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: version must be MAJOR.MINOR.PATCH (e.g. 1.2.3)" >&2
    exit 1
fi

# Detect current version from the root package.json
CURRENT=$(grep -oP '"version":\s*"\K[^"]+' "$ROOT/package.json")
echo "Bumping $CURRENT -> $VERSION"

# ── package.json (root) ──────────────────────────────────────────
sed -i "s/\"version\": \"$CURRENT\"/\"version\": \"$VERSION\"/" "$ROOT/package.json"
echo "  package.json"

# ── packages/core/pyproject.toml ────────────────────────────────
sed -i "s/^version = \"$CURRENT\"/version = \"$VERSION\"/" "$ROOT/packages/core/pyproject.toml"
echo "  packages/core/pyproject.toml"

# ── packages/core/src/rs3tk_core/__init__.py ────────────────────
sed -i "s/__version__ = \"$CURRENT\"/__version__ = \"$VERSION\"/" "$ROOT/packages/core/src/rs3tk_core/__init__.py"
echo "  packages/core/src/rs3tk_core/__init__.py"

# ── packages/cli/pyproject.toml ─────────────────────────────────
sed -i "s/^version = \"$CURRENT\"/version = \"$VERSION\"/" "$ROOT/packages/cli/pyproject.toml"
echo "  packages/cli/pyproject.toml"

# ── packages/electron/package.json ──────────────────────────────
sed -i "s/\"version\": \"$CURRENT\"/\"version\": \"$VERSION\"/" "$ROOT/packages/electron/package.json"
echo "  packages/electron/package.json"

# ── packages/electron/pyproject.toml ────────────────────────────
sed -i "s/^version = \"$CURRENT\"/version = \"$VERSION\"/" "$ROOT/packages/electron/pyproject.toml"
echo "  packages/electron/pyproject.toml"

# ── packages/electron/requirements.txt ──────────────────────────
sed -i "s/rs3tk-core==$CURRENT/rs3tk-core==$VERSION/" "$ROOT/packages/electron/requirements.txt"
echo "  packages/electron/requirements.txt"

# ── packaging/rpm/rs3tk.spec ────────────────────────────────────
sed -i "s/^Version:        $CURRENT/Version:        $VERSION/" "$ROOT/packaging/rpm/rs3tk.spec"
echo "  packaging/rpm/rs3tk.spec"

# ── packaging/rpm/rs3tk-electron.spec ───────────────────────────
sed -i "s/^Version:        $CURRENT/Version:        $VERSION/" "$ROOT/packaging/rpm/rs3tk-electron.spec"
echo "  packaging/rpm/rs3tk-electron.spec"

# ── packaging/alpine/APKBUILD ───────────────────────────────────
sed -i "s/^pkgver=$CURRENT/pkgver=$VERSION/" "$ROOT/packaging/alpine/APKBUILD"
echo "  packaging/alpine/APKBUILD"

# ── packaging/arch/PKGBUILD ────────────────────────────────────
sed -i "s/^pkgver=$CURRENT/pkgver=$VERSION/" "$ROOT/packaging/arch/PKGBUILD"
echo "  packaging/arch/PKGBUILD"

# ── packaging/arch/python-rs3tk/PKGBUILD ────────────────────────
sed -i "s/^pkgver=$CURRENT/pkgver=$VERSION/" "$ROOT/packaging/arch/python-rs3tk/PKGBUILD"
echo "  packaging/arch/python-rs3tk/PKGBUILD"

# ── packaging/deb/debian/changelog ──────────────────────────────
# Update the version in the changelog (first line after package name)
sed -i "0,/^rs3tk ($CURRENT/s/^rs3tk ($CURRENT/rs3tk ($VERSION/" "$ROOT/packaging/deb/debian/changelog"
echo "  packaging/deb/debian/changelog"

# ── regenerate lockfiles ────────────────────────────────────────
echo "Regenerating lockfiles..."
(cd "$ROOT" && uv lock --quiet)
(cd "$ROOT" && pnpm install --no-frozen-lockfile --silent 2>/dev/null)

echo "Done. Version is now $VERSION"