#!/usr/bin/env bash
# Build and test rs3tk packages for various Linux distributions.
#
# Usage:
#   ./scripts/package-linux.sh              # Build all packages
#   ./scripts/package-linux.sh --build      # Build packages only
#   ./scripts/package-linux.sh --test       # Test packages only
#   ./scripts/package-linux.sh --deb        # Build/test DEB only
#   ./scripts/package-linux.sh --rpm        # Build/test RPM only
#   ./scripts/package-linux.sh --apk        # Build/test APK only
#   ./scripts/package-linux.sh --arch       # Build/test Arch only
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION=$(grep -oP '^version = "\K[^"]+' "$ROOT/packages/cli/pyproject.toml")
BUILD_DIR="$ROOT/build/packages"
TEST_DIR="$ROOT/build/test-results"

# ── Parse arguments ────────────────────────────────────────────────
DO_BUILD=true
DO_TEST=true
BUILD_DEB=false
BUILD_RPM=false
BUILD_APK=false
BUILD_ARCH=false

for arg in "$@"; do
    case "$arg" in
        --build) DO_TEST=false ;;
        --test)  DO_BUILD=false ;;
        --deb)   BUILD_DEB=true ;;
        --rpm)   BUILD_RPM=true ;;
        --apk)   BUILD_APK=true ;;
        --arch)  BUILD_ARCH=true ;;
        *)       echo "Unknown flag: $arg"; exit 1 ;;
    esac
done

# If no specific format selected, build all
if ! $BUILD_DEB && ! $BUILD_RPM && ! $BUILD_APK && ! $BUILD_ARCH; then
    BUILD_DEB=true
    BUILD_RPM=true
    BUILD_APK=true
    BUILD_ARCH=true
fi

# ── Setup directories ──────────────────────────────────────────────
mkdir -p "$BUILD_DIR" "$TEST_DIR"

# ── Build Python wheels first ──────────────────────────────────────
if $DO_BUILD; then
    echo "==> Building Python wheels..."
    cd "$ROOT"
    uv build --wheel --out-dir "$BUILD_DIR/wheels" packages/core/
    uv build --wheel --out-dir "$BUILD_DIR/wheels" packages/cli/
    echo "    Wheels built in $BUILD_DIR/wheels/"
fi

# ── Build DEB package ─────────────────────────────────────────────
build_deb() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Building DEB package (Ubuntu/Debian)"
    echo "═══════════════════════════════════════════════════════════════"

    local DEB_DIR="$BUILD_DIR/deb"
    mkdir -p "$DEB_DIR"

    # Use Docker to build in a clean Ubuntu environment
    docker run --rm \
        -v "$ROOT:/src:ro" \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        -v "$DEB_DIR:/output" \
        ubuntu:24.04 \
        bash -c '
            set -euo pipefail
            export DEBIAN_FRONTEND=noninteractive

            # Install build dependencies
            apt-get update && apt-get install -y --no-install-recommends \
                build-essential \
                fakeroot \
                dpkg-dev

            # Create package structure for a single combined .deb
            PKG_DIR="/tmp/rs3tk_'"$VERSION"'_all"
            mkdir -p "$PKG_DIR/DEBIAN"
            mkdir -p "$PKG_DIR/usr/lib/python3/dist-packages"
            mkdir -p "$PKG_DIR/usr/bin"

            # Create control file (single package with bundled deps)
            cat > "$PKG_DIR/DEBIAN/control" << EOF
Package: rs3tk
Version: '"$VERSION"'
Section: python
Priority: optional
Architecture: all
Maintainer: Caleb <caleb.andrew.whiting@gmail.com>
Depends: python3 (>= 3.11), python3-httpx, python3-pydantic, python3-keyring, python3-click, python3-rich
Description: Open-source Jagex Launcher replacement for Linux
 rs3tk is an open-source implementation of the Jagex Launcher.
 It authenticates via OAuth2, manages game sessions, and launches
 RS3/OSRS clients (Official, RuneLite, HDOS).
 .
 This package provides the command-line interface and Rich terminal UI.
EOF

            # Install all wheels (core + CLI)
            for whl in /wheels/*.whl; do
                pip3 install --no-deps --target="$PKG_DIR/usr/lib/python3/dist-packages" "$whl"
            done

            # Create entry point script
            cat > "$PKG_DIR/usr/bin/rs3tk" << '"'"'ENTRY'"'"'
#!/usr/bin/env python3
from rs3tk_cli.cli import main
if __name__ == "__main__":
    main()
ENTRY
            chmod 755 "$PKG_DIR/usr/bin/rs3tk"

            # Build package
            cd /tmp
            fakeroot dpkg-deb --build "rs3tk_'"$VERSION"'_all"
            cp "rs3tk_'"$VERSION"'_all.deb" /output/

            echo "DEB package built successfully"
        '

    echo "    DEB package: $DEB_DIR/rs3tk_${VERSION}_all.deb"
}

# ── Build RPM package ─────────────────────────────────────────────
build_rpm() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Building RPM package (Fedora/RHEL)"
    echo "═══════════════════════════════════════════════════════════════"

    local RPM_DIR="$BUILD_DIR/rpm"
    mkdir -p "$RPM_DIR"

    # Use Docker to build in a clean Fedora environment
    docker run --rm \
        -v "$ROOT:/src:ro" \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        -v "$RPM_DIR:/output" \
        fedora:40 \
        bash -c '
            set -euo pipefail

            # Install build dependencies
            dnf install -y \
                rpm-build \
                python3-devel \
                python3-setuptools \
                python3-pip \
                python3-wheel \
                python3-httpx \
                python3-pydantic \
                python3-keyring \
                python3-click \
                python3-rich

            # Setup RPM build tree
            mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

            # Copy wheels as sources
            cp /wheels/*.whl ~/rpmbuild/SOURCES/

            # Create spec file for a single combined package
            cat > ~/rpmbuild/SPECS/rs3tk.spec << EOF
Name:           python3-rs3tk
Version:        '"$VERSION"'
Release:        1%{?dist}
Summary:        Open-source Jagex Launcher replacement for Linux

License:        MIT
URL:            https://github.com/CalebWhiting/rs3tk
Source0:        rs3tk-'"$VERSION"'-py3-none-any.whl
Source1:        rs3tk_core-'"$VERSION"'-py3-none-any.whl

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
Requires:       python3-httpx >= 0.27
Requires:       python3-pydantic >= 2.0
Requires:       python3-keyring >= 25.0
Requires:       python3-click >= 8.1
Requires:       python3-rich >= 13.0

%description
rs3tk is an open-source implementation of the Jagex Launcher.
It authenticates via OAuth2, manages game sessions, and launches
RS3/OSRS clients (Official, RuneLite, HDOS).

%prep
# No prep needed for wheel-based package

%build
# No build needed for wheel-based package

%install
mkdir -p %{buildroot}%{python3_sitelib}
pip3 install --no-deps --root=%{buildroot} %{_sourcedir}/*.whl

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/rs3tk_core/
%{python3_sitelib}/rs3tk_cli/
%{python3_sitelib}/rs3tk-*.dist-info/
%{python3_sitelib}/rs3tk_core-*.dist-info/
%{_bindir}/rs3tk

%changelog
* Sat Aug 01 2026 Caleb <caleb.andrew.whiting@gmail.com> - '"$VERSION"'-1
- Initial package
EOF

            # Build RPM
            cd ~/rpmbuild
            rpmbuild -ba SPECS/rs3tk.spec

            # Copy RPMs to output
            cp RPMS/noarch/*.rpm /output/
            cp SRPMS/*.rpm /output/

            echo "RPM package built successfully"
        '

    echo "    RPM packages: $RPM_DIR/python3-rs3tk-${VERSION}-1.*.rpm"
}

# ── Build APK package ─────────────────────────────────────────────
build_apk() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Building APK package (Alpine Linux)"
    echo "═══════════════════════════════════════════════════════════════"

    local APK_DIR="$BUILD_DIR/apk"
    mkdir -p "$APK_DIR"

    # Use Docker to build in a clean Alpine environment
    docker run --rm \
        -v "$ROOT:/src:ro" \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        -v "$APK_DIR:/output" \
        alpine:3.20 \
        sh -c '
            set -euo pipefail

            # Install build dependencies
            apk add --no-cache \
                python3 \
                py3-pip \
                py3-setuptools \
                py3-build \
                py3-installer \
                py3-httpx \
                py3-pydantic \
                py3-keyring \
                py3-click \
                py3-rich

            # Detect Python version
            PY_VER=$(python3 -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")")

            # Create package directory
            PKG_DIR="/tmp/pkg-rs3tk"
            mkdir -p "$PKG_DIR/usr/lib/python${PY_VER}/site-packages"
            mkdir -p "$PKG_DIR/usr/bin"

            # Install all wheels
            for whl in /wheels/*.whl; do
                pip3 install --no-deps --target="$PKG_DIR/usr/lib/python${PY_VER}/site-packages" "$whl"
            done

            # Create entry point script
            cat > "$PKG_DIR/usr/bin/rs3tk" << '"'"'ENTRY'"'"'
#!/usr/bin/env python3
from rs3tk_cli.cli import main
if __name__ == "__main__":
    main()
ENTRY
            chmod 755 "$PKG_DIR/usr/bin/rs3tk"

            echo "APK package structure created at $PKG_DIR"
            echo "Note: Full APK build requires abuild and alpine-sdk"
        '

    echo "    APK package: $APK_DIR/"
}

# ── Build Arch package ────────────────────────────────────────────
build_arch() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Building Arch Linux package"
    echo "═══════════════════════════════════════════════════════════════"

    local ARCH_DIR="$BUILD_DIR/arch"
    mkdir -p "$ARCH_DIR"

    # Use Docker to build in a clean Arch environment
    docker run --rm \
        -v "$ROOT:/src:ro" \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        -v "$ARCH_DIR:/output" \
        archlinux:latest \
        bash -c '
            set -euo pipefail

            # Install build dependencies
            pacman -Sy --noconfirm \
                python \
                python-build \
                python-installer \
                python-setuptools \
                python-httpx \
                python-pydantic \
                python-keyring \
                python-click \
                python-rich

            # Detect Python version
            PY_VER=$(python3 -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")")

            # Create package directory
            PKG_DIR="/tmp/pkg-rs3tk"
            mkdir -p "$PKG_DIR/usr/lib/python${PY_VER}/site-packages"
            mkdir -p "$PKG_DIR/usr/bin"

            # Install all wheels
            for whl in /wheels/*.whl; do
                pip3 install --no-deps --target="$PKG_DIR/usr/lib/python${PY_VER}/site-packages" "$whl"
            done

            # Create entry point script
            cat > "$PKG_DIR/usr/bin/rs3tk" << '"'"'ENTRY'"'"'
#!/usr/bin/env python3
from rs3tk_cli.cli import main
if __name__ == "__main__":
    main()
ENTRY
            chmod 755 "$PKG_DIR/usr/bin/rs3tk"

            echo "Arch package structure created at $PKG_DIR"
            echo "Note: Full Arch build requires makepkg and devtools"
        '

    echo "    Arch package: $ARCH_DIR/"
}

# ── Test packages in containers ───────────────────────────────────
test_packages() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Testing packages in fresh containers"
    echo "═══════════════════════════════════════════════════════════════"

    local PASSED=0
    local FAILED=0

    # Test DEB on Ubuntu 24.04
    if [ -f "$BUILD_DIR/deb/rs3tk_${VERSION}_all.deb" ]; then
        echo ""
        echo "Testing DEB on Ubuntu 24.04..."
        if docker run --rm --network=host \
            -v "$BUILD_DIR/deb:/pkg:ro" \
            ubuntu:24.04 \
            bash -c '
                set -euo pipefail
                export DEBIAN_FRONTEND=noninteractive
                apt-get update && apt-get install -y /pkg/rs3tk_'"$VERSION"'_all.deb
                rs3tk --version
            ' > "$TEST_DIR/deb-ubuntu24.04.log" 2>&1; then
            echo "    ✓ DEB test passed (Ubuntu 24.04)"
            PASSED=$((PASSED + 1))
        else
            echo "    ✗ DEB test failed (Ubuntu 24.04)"
            cat "$TEST_DIR/deb-ubuntu24.04.log"
            FAILED=$((FAILED + 1))
        fi
    fi

    # Test DEB on Debian 12
    if [ -f "$BUILD_DIR/deb/rs3tk_${VERSION}_all.deb" ]; then
        echo ""
        echo "Testing DEB on Debian 12..."
        if docker run --rm --network=host \
            -v "$BUILD_DIR/deb:/pkg:ro" \
            debian:12 \
            bash -c '
                set -euo pipefail
                export DEBIAN_FRONTEND=noninteractive
                apt-get update && apt-get install -y /pkg/rs3tk_'"$VERSION"'_all.deb
                rs3tk --version
            ' > "$TEST_DIR/deb-debian12.log" 2>&1; then
            echo "    ✓ DEB test passed (Debian 12)"
            PASSED=$((PASSED + 1))
        else
            echo "    ✗ DEB test failed (Debian 12)"
            cat "$TEST_DIR/deb-debian12.log"
            FAILED=$((FAILED + 1))
        fi
    fi

    # Test RPM on Fedora 40
    if ls "$BUILD_DIR/rpm"/python3-rs3tk-*.rpm >/dev/null 2>&1; then
        echo ""
        echo "Testing RPM on Fedora 40..."
        if docker run --rm --network=host \
            -v "$BUILD_DIR/rpm:/pkg:ro" \
            fedora:40 \
            bash -c '
                set -euo pipefail
                dnf install -y /pkg/python3-rs3tk-*.rpm
                rs3tk --version
            ' > "$TEST_DIR/rpm-fedora40.log" 2>&1; then
            echo "    ✓ RPM test passed (Fedora 40)"
            PASSED=$((PASSED + 1))
        else
            echo "    ✗ RPM test failed (Fedora 40)"
            cat "$TEST_DIR/rpm-fedora40.log"
            FAILED=$((FAILED + 1))
        fi
    fi

    # Test pip on Alpine 3.20
    echo ""
    echo "Testing pip install on Alpine 3.20..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        alpine:3.20 \
        sh -c '
            set -euo pipefail
            apk add --no-cache python3 py3-pip py3-httpx py3-pydantic py3-keyring py3-click py3-rich
            pip3 install --break-system-packages --no-deps /wheels/*.whl
            rs3tk --version
        ' > "$TEST_DIR/pip-alpine3.20.log" 2>&1; then
        echo "    ✓ pip test passed (Alpine 3.20)"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ pip test failed (Alpine 3.20)"
        cat "$TEST_DIR/pip-alpine3.20.log"
        FAILED=$((FAILED + 1))
    fi

    # Test pip on Arch Linux
    echo ""
    echo "Testing pip install on Arch Linux..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        archlinux:latest \
        bash -c '
            set -euo pipefail
            pacman -Sy --noconfirm python python-pip python-httpx python-pydantic python-keyring python-click python-rich
            pip3 install --break-system-packages --no-deps /wheels/*.whl
            rs3tk --version
        ' > "$TEST_DIR/pip-archlinux.log" 2>&1; then
        echo "    ✓ pip test passed (Arch Linux)"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ pip test failed (Arch Linux)"
        cat "$TEST_DIR/pip-archlinux.log"
        FAILED=$((FAILED + 1))
    fi

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Test Results: $PASSED passed, $FAILED failed"
    echo "═══════════════════════════════════════════════════════════════"

    if [ $FAILED -gt 0 ]; then
        echo "Some tests failed. Check logs in $TEST_DIR/"
        exit 1
    fi

    echo "All tests passed!"
}

# ── Main execution ────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════════"
echo "  rs3tk Linux Package Builder"
echo "  Version: $VERSION"
echo "═══════════════════════════════════════════════════════════════"

if $DO_BUILD; then
    $BUILD_DEB && build_deb
    $BUILD_RPM && build_rpm
    $BUILD_APK && build_apk
    $BUILD_ARCH && build_arch
fi

if $DO_TEST; then
    test_packages
fi

echo ""
echo "Done! Packages are in: $BUILD_DIR/"
echo "Test logs are in: $TEST_DIR/"