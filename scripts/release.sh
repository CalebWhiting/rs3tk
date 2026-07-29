#!/usr/bin/env bash
# Tag and push a release. CI will build the AppImage and publish to PyPI.
#
# Usage:
#   ./scripts/release.sh 1.2.3
#
# Steps:
#   1. Bump version across all packages (via bump-version.sh)
#   2. Commit the version bump
#   3. Tag the commit (v1.2.3)
#   4. Push commit + tag
#
# The tag push triggers the release workflow which:
#   - Publishes rs3tk-core and rs3tk to PyPI
#   - Builds the AppImage and attaches it to the Codeberg Release
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <version>" >&2
    echo "Example: $0 1.2.3" >&2
    exit 1
fi

VERSION="$1"
TAG="v$VERSION"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: version must be MAJOR.MINOR.PATCH (e.g. 1.2.3)" >&2
    exit 1
fi

# Check working tree is clean
if ! git -C "$ROOT" diff --quiet || ! git -C "$ROOT" diff --cached --quiet; then
    echo "Error: working tree is dirty. Commit or stash changes first." >&2
    exit 1
fi

# Check tag doesn't already exist
if git -C "$ROOT" rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Error: tag $TAG already exists." >&2
    exit 1
fi

# Bump version
"$SCRIPT_DIR/bump-version.sh" "$VERSION"

# Commit
git -C "$ROOT" add -A
git -C "$ROOT" commit -m "v$VERSION"

# Tag
git -C "$ROOT" tag "$TAG"

# Push
echo "Pushing commit and tag..."
git -C "$ROOT" push
git -C "$ROOT" push origin "$TAG"

echo ""
echo "Released $TAG"
echo "  CI will build the AppImage and publish to PyPI."
echo "  Track progress: git log --oneline --decorate"
