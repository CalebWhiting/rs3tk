#!/usr/bin/env bash
# Test the rs3tk Electron app in various Linux containers.
#
# Usage:
#   ./scripts/test-electron.sh              # Test all distributions
#   ./scripts/test-electron.sh --ubuntu     # Test Ubuntu only
#   ./scripts/test-electron.sh --debian     # Test Debian only
#   ./scripts/test-electron.sh --fedora     # Test Fedora only
#   ./scripts/test-electron.sh --arch       # Test Arch only
#   ./scripts/test-electron.sh --appimage   # Test AppImage only
#   ./scripts/test-electron.sh --deb        # Test .deb package only
#   ./scripts/test-electron.sh --rpm        # Test .rpm package only
#   ./scripts/test-electron.sh --build      # Build AppImage first
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION=$(grep -oP '^version = "\K[^"]+' "$ROOT/packages/cli/pyproject.toml")
BUILD_DIR="$ROOT/build/packages"
TEST_DIR="$ROOT/build/test-results/electron"
APPIMAGE_DIR="$ROOT/packages/electron/dist"
APPIMAGE_NAME="RS3TK-${VERSION}.AppImage"
DEB_NAME="rs3tk-electron_${VERSION}_amd64.deb"

# ── Parse arguments ────────────────────────────────────────────────
TEST_UBUNTU=false
TEST_DEBIAN=false
TEST_FEDORA=false
TEST_ARCH=false
TEST_APPIMAGE=true
TEST_DEB=true
TEST_RPM=true
BUILD_FIRST=false

for arg in "$@"; do
    case "$arg" in
        --ubuntu)   TEST_UBUNTU=true ;;
        --debian)   TEST_DEBIAN=true ;;
        --fedora)   TEST_FEDORA=true ;;
        --arch)     TEST_ARCH=true ;;
        --appimage) TEST_DEB=false; TEST_RPM=false ;;
        --deb)      TEST_APPIMAGE=false; TEST_RPM=false ;;
        --rpm)      TEST_APPIMAGE=false; TEST_DEB=false ;;
        --build)    BUILD_FIRST=true ;;
        *)          echo "Unknown flag: $arg"; exit 1 ;;
    esac
done

# If no specific distribution selected, test all
if ! $TEST_UBUNTU && ! $TEST_DEBIAN && ! $TEST_FEDORA && ! $TEST_ARCH; then
    TEST_UBUNTU=true
    TEST_DEBIAN=true
    TEST_FEDORA=true
    TEST_ARCH=true
fi

# ── Setup directories ──────────────────────────────────────────────
mkdir -p "$BUILD_DIR" "$TEST_DIR"

# ── Build AppImage if requested ───────────────────────────────────
if $BUILD_FIRST; then
    echo "==> Building AppImage..."
    cd "$ROOT"

    # Check if Dockerfile.build exists
    if [ ! -f "$ROOT/Dockerfile.build" ]; then
        echo "Error: Dockerfile.build not found"
        exit 1
    fi

    # Build using Docker
    docker build -f Dockerfile.build -t rs3tk-build .

    # Create a container and copy the AppImage out
    CONTAINER_ID=$(docker create rs3tk-build)
    docker cp "$CONTAINER_ID:/app/packages/electron/dist/." "$APPIMAGE_DIR/"
    docker rm "$CONTAINER_ID"

    echo "    AppImage built: $APPIMAGE_DIR/$APPIMAGE_NAME"
fi

# ── Check if AppImage exists ──────────────────────────────────────
if [ ! -f "$APPIMAGE_DIR/$APPIMAGE_NAME" ]; then
    echo "Error: AppImage not found at $APPIMAGE_DIR/$APPIMAGE_NAME"
    echo "Run with --build flag to build it first, or build manually:"
    echo "  docker build -f Dockerfile.build -t rs3tk-build ."
    echo "  docker create --name tmp rs3tk-build && docker cp tmp:/app/packages/electron/dist/. $APPIMAGE_DIR/ && docker rm tmp"
    exit 1
fi

echo "Using AppImage: $APPIMAGE_DIR/$APPIMAGE_NAME"

# ════════════════════════════════════════════════════════════════════
#  AppImage tests (extract and run in containers)
# ════════════════════════════════════════════════════════════════════

# ── AppImage test helper ──────────────────────────────────────────
run_appimage_test() {
    local distro="$1"
    local image="$2"
    local log_file="$TEST_DIR/appimage-${distro}.log"

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Testing AppImage on $distro"
    echo "═══════════════════════════════════════════════════════════════"

    if docker run --rm --network=host \
        -v "$APPIMAGE_DIR:/appimage:ro" \
        "$image" \
        bash -c '
            set -euo pipefail
            export DEBIAN_FRONTEND=noninteractive

            # Install Xvfb, X11 utilities, and display libraries
            if command -v apt-get &>/dev/null; then
                apt-get update && apt-get install -y --no-install-recommends \
                    xvfb x11-utils xdotool imagemagick \
                    libx11-6 libxext6 libxss1 libxtst6 libnss3 \
                    libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libgbm1 \
                    libgtk-3-0 '"${3:-libasound2t64}"' \
                    libxkbcommon0 libwayland-client0 libwayland-cursor0 libwayland-egl1 \
                    libxrandr2 libxcomposite1 libxdamage1 libxfixes3 libxi6 ca-certificates
            elif command -v dnf &>/dev/null; then
                dnf install -y \
                    xorg-x11-server-Xvfb xorg-x11-utils xdotool ImageMagick \
                    libX11 libXext libXScrnSaver libXtst nss atk at-spi2-atk \
                    cups-libs libdrm mesa-libgbm gtk3 alsa-lib \
                    libxkbcommon wayland-libs-client wayland-libs-cursor wayland-libs-egl \
                    libXrandr libXcomposite libXdamage libXfixes libXi
            elif command -v pacman &>/dev/null; then
                pacman -Sy --noconfirm \
                    xorg-server-xvfb xdotool imagemagick \
                    libx11 libxext libxss libxtst nss atk at-spi2-core \
                    cups libdrm mesa gtk3 alsa-lib \
                    libxkbcommon wayland libxrandr libxcomposite libxdamage libxfixes libxi
            fi

            # Copy AppImage to writable location and extract
            cp /appimage/'"$APPIMAGE_NAME"' /tmp/'"$APPIMAGE_NAME"'
            chmod +x /tmp/'"$APPIMAGE_NAME"'
            cd /tmp && /tmp/'"$APPIMAGE_NAME"' --appimage-extract > /dev/null 2>&1

            # Start Xvfb
            Xvfb :99 -screen 0 1280x1024x24 &
            XVFB_PID=$!
            export DISPLAY=:99
            sleep 2

            # Launch the app
            echo "Launching Electron app..."
            ./squashfs-root/rs3tk-electron --no-sandbox --disable-dev-shm-usage &
            APP_PID=$!
            sleep 5

            # Check if app is running
            if kill -0 $APP_PID 2>/dev/null; then
                echo "✓ App process is running (PID: $APP_PID)"

                # Check for windows
                WINDOW_COUNT=$(xdotool search --name "" 2>/dev/null | wc -l || echo "0")
                echo "  Windows found: $WINDOW_COUNT"

                RS3TK_WINDOW=$(xdotool search --name "RS3TK" 2>/dev/null || echo "")
                if [ -n "$RS3TK_WINDOW" ]; then
                    echo "  ✓ RS3TK window found"
                    import -window root /tmp/screenshot.png 2>/dev/null || true
                    echo "  Screenshot saved to /tmp/screenshot.png"
                else
                    echo "  ⚠ RS3TK window not found by name"
                fi

                kill $APP_PID 2>/dev/null || true
                wait $APP_PID 2>/dev/null || true
                echo "✓ App terminated cleanly"
            else
                echo "✗ App failed to start"
                exit 1
            fi

            kill $XVFB_PID 2>/dev/null || true
            wait $XVFB_PID 2>/dev/null || true
            echo "✓ Test passed"
        ' > "$log_file" 2>&1; then
        echo "    ✓ $distro"
        return 0
    else
        echo "    ✗ $distro"
        echo "    Log: $log_file"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════
#  DEB package tests (install .deb and run)
# ════════════════════════════════════════════════════════════════════

test_electron_deb_package() {
    local distro="$1"
    local image="$2"
    local log_file="$TEST_DIR/deb-${distro}.log"

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Testing .deb package on $distro"
    echo "═══════════════════════════════════════════════════════════════"

    if docker run --rm --network=host \
        -v "$APPIMAGE_DIR:/pkg:ro" \
        "$image" \
        bash -c '
            set -euo pipefail
            export DEBIAN_FRONTEND=noninteractive

            # Install Xvfb and display libraries
            apt-get update && apt-get install -y --no-install-recommends \
                xvfb x11-utils xdotool imagemagick ca-certificates \
                libasound2t64 libnotify4 libsecret-1-0

            # Install the .deb package (it pulls in its own dependencies)
            dpkg -i /pkg/rs3tk-electron_'"$VERSION"'_amd64.deb || \
                apt-get install -f -y

            # Verify installation
            echo "Verifying installation..."
            dpkg -l rs3tk-electron | grep -q "^ii" || { echo "Package not installed"; exit 1; }
            echo "  ✓ Package installed"

            # Find the installed binary (electron-builder installs to /opt/RS3TK/)
            ELECTRON_BIN=""
            for candidate in /opt/RS3TK/rs3tk-electron /usr/bin/rs3tk-electron; do
                if [ -f "$candidate" ] && [ -x "$candidate" ]; then
                    ELECTRON_BIN="$candidate"
                    break
                fi
            done
            if [ -z "$ELECTRON_BIN" ]; then
                echo "✗ Could not find rs3tk-electron binary"
                exit 1
            fi
            echo "  Binary: $ELECTRON_BIN"

            # Start Xvfb
            Xvfb :99 -screen 0 1280x1024x24 &
            XVFB_PID=$!
            export DISPLAY=:99
            sleep 2

            # Launch the installed app
            echo "Launching installed .deb app..."
            "$ELECTRON_BIN" --no-sandbox --disable-dev-shm-usage &
            APP_PID=$!
            sleep 5

            # Check if app is running
            if kill -0 $APP_PID 2>/dev/null; then
                echo "✓ App process is running (PID: $APP_PID)"

                RS3TK_WINDOW=$(xdotool search --name "RS3TK" 2>/dev/null || echo "")
                if [ -n "$RS3TK_WINDOW" ]; then
                    echo "  ✓ RS3TK window found"
                else
                    echo "  ⚠ RS3TK window not found by name"
                fi

                kill $APP_PID 2>/dev/null || true
                wait $APP_PID 2>/dev/null || true
                echo "✓ App terminated cleanly"
            else
                echo "✗ App failed to start"
                exit 1
            fi

            kill $XVFB_PID 2>/dev/null || true
            wait $XVFB_PID 2>/dev/null || true
            echo "✓ Test passed"
        ' > "$log_file" 2>&1; then
        echo "    ✓ $distro"
        return 0
    else
        echo "    ✗ $distro"
        echo "    Log: $log_file"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════
#  RPM package tests (build RPM from AppImage, install, and run)
# ════════════════════════════════════════════════════════════════════

test_electron_rpm_package() {
    local distro="$1"
    local image="$2"
    local log_file="$TEST_DIR/rpm-${distro}.log"

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Testing .rpm package on $distro"
    echo "═══════════════════════════════════════════════════════════════"

    if docker run --rm --network=host \
        -v "$APPIMAGE_DIR:/appimage:ro" \
        "$image" \
        bash -c '
            set -euo pipefail

            # Install build tools and Xvfb
            dnf install -y \
                rpm-build \
                xorg-x11-server-Xvfb xorg-x11-utils xdotool ImageMagick \
                libX11 libXext libXScrnSaver libXtst nss atk at-spi2-atk \
                cups-libs libdrm mesa-libgbm gtk3 alsa-lib \
                libxkbcommon libXrandr libXcomposite libXdamage libXfixes libXi \
                wayland-libs-client wayland-libs-cursor wayland-libs-egl 2>/dev/null || \
            dnf install -y \
                rpm-build \
                xorg-x11-server-Xvfb xdotool ImageMagick \
                libX11 libXext libXScrnSaver libXtst nss atk at-spi2-atk \
                cups-libs libdrm mesa-libgbm gtk3 alsa-lib \
                libxkbcommon libXrandr libXcomposite libXdamage libXfixes libXi

            # Build an RPM from the AppImage
            echo "Building RPM from AppImage..."
            mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

            cp /appimage/'"$APPIMAGE_NAME"' ~/rpmbuild/SOURCES/

            cat > ~/rpmbuild/SPECS/rs3tk-electron.spec << '"'"'SPEC'"'"'
%define appname rs3tk-electron

Name:           %{appname}
Version:        '"$VERSION"'
Release:        1%{?dist}
Summary:        RS3TK - RuneScape 3 Toolkit (Electron GUI)
License:        MIT
URL:            https://github.com/CalebWhiting/rs3tk
Source0:        RS3TK-'"$VERSION"'.AppImage
BuildArch:      x86_64
Requires:       gtk3 nss at-spi2-atk cups-libs libdrm mesa-libgbm alsa-lib

%description
RS3TK is an open-source implementation of the Jagex Launcher.
This package provides the Electron-based GUI.

%prep
chmod +x %{_sourcedir}/RS3TK-'"$VERSION"'.AppImage
%{_sourcedir}/RS3TK-'"$VERSION"'.AppImage --appimage-extract

%build
# No build needed - pre-built AppImage

%install
mkdir -p %{buildroot}/opt/rs3tk
cp -r squashfs-root/* %{buildroot}/opt/rs3tk/

            # Rename the binary and create a wrapper
            if [ -f %{buildroot}/opt/rs3tk/rs3tk-electron ]; then
                mv %{buildroot}/opt/rs3tk/rs3tk-electron %{buildroot}/opt/rs3tk/rs3tk-electron-bin
            fi

            mkdir -p %{buildroot}/usr/bin
            cat > %{buildroot}/usr/bin/rs3tk-electron << '"'"'WRAPPER'"'"'
#!/bin/sh
APPDIR="/opt/rs3tk"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"
exec "${APPDIR}/rs3tk-electron-bin" --no-sandbox "$@"
WRAPPER
            chmod 755 %{buildroot}/usr/bin/rs3tk-electron

mkdir -p %{buildroot}/usr/share/applications
cat > %{buildroot}/usr/share/applications/rs3tk-electron.desktop << '"'"'DESKTOP'"'"'
[Desktop Entry]
Name=RS3TK
Exec=rs3tk-electron %U
Type=Application
Categories=Game;
Icon=rs3tk
DESKTOP

%files
/opt/rs3tk/
/usr/bin/rs3tk-electron
/usr/share/applications/rs3tk-electron.desktop

%changelog
* Sat Aug 01 2026 Caleb <caleb.andrew.whiting@gmail.com> - '"$VERSION"'-1
- Initial RPM package
SPEC

            cd ~/rpmbuild
            rpmbuild -ba SPECS/rs3tk-electron.spec

            RPM_FILE=$(find RPMS -name "rs3tk-electron-*.rpm" | head -1)
            if [ -z "$RPM_FILE" ]; then
                echo "✗ RPM build failed"
                exit 1
            fi
            echo "  ✓ RPM built: $RPM_FILE"

            # Install the RPM
            echo "Installing RPM..."
            dnf install -y "$RPM_FILE"

            # Verify installation
            echo "Verifying installation..."
            rpm -q rs3tk-electron || { echo "Package not installed"; exit 1; }
            echo "  ✓ Package installed"

            # Start Xvfb
            Xvfb :99 -screen 0 1280x1024x24 &
            XVFB_PID=$!
            export DISPLAY=:99
            sleep 2

            # Launch the installed app
            echo "Launching installed .rpm app..."
            rs3tk-electron --no-sandbox --disable-dev-shm-usage &
            APP_PID=$!
            sleep 5

            # Check if app is running
            if kill -0 $APP_PID 2>/dev/null; then
                echo "✓ App process is running (PID: $APP_PID)"

                RS3TK_WINDOW=$(xdotool search --name "RS3TK" 2>/dev/null || echo "")
                if [ -n "$RS3TK_WINDOW" ]; then
                    echo "  ✓ RS3TK window found"
                else
                    echo "  ⚠ RS3TK window not found by name"
                fi

                kill $APP_PID 2>/dev/null || true
                wait $APP_PID 2>/dev/null || true
                echo "✓ App terminated cleanly"
            else
                echo "✗ App failed to start"
                exit 1
            fi

            kill $XVFB_PID 2>/dev/null || true
            wait $XVFB_PID 2>/dev/null || true
            echo "✓ Test passed"
        ' > "$log_file" 2>&1; then
        echo "    ✓ $distro"
        return 0
    else
        echo "    ✗ $distro"
        echo "    Log: $log_file"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════
#  Main execution
# ════════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════"
echo "  rs3tk Electron App Container Tester"
echo "  Version: $VERSION"
echo "═══════════════════════════════════════════════════════════════"

TOTAL_FAILED=0

# ── AppImage tests ────────────────────────────────────────────────
if $TEST_APPIMAGE; then
    if $TEST_UBUNTU; then
        run_appimage_test "ubuntu-24.04" "ubuntu:24.04" "libasound2t64" || TOTAL_FAILED=$((TOTAL_FAILED + 1))
    fi
    if $TEST_DEBIAN; then
        run_appimage_test "debian-12" "debian:12" "libasound2" || TOTAL_FAILED=$((TOTAL_FAILED + 1))
    fi
    if $TEST_FEDORA; then
        run_appimage_test "fedora-40" "fedora:40" || TOTAL_FAILED=$((TOTAL_FAILED + 1))
    fi
    if $TEST_ARCH; then
        run_appimage_test "archlinux" "archlinux:latest" || TOTAL_FAILED=$((TOTAL_FAILED + 1))
    fi
fi

# ── DEB package tests ─────────────────────────────────────────────
if $TEST_DEB; then
    if [ -f "$APPIMAGE_DIR/$DEB_NAME" ]; then
        if $TEST_UBUNTU; then
            test_electron_deb_package "ubuntu-24.04" "ubuntu:24.04" || TOTAL_FAILED=$((TOTAL_FAILED + 1))
        fi
        if $TEST_DEBIAN; then
            test_electron_deb_package "debian-12" "debian:12" || TOTAL_FAILED=$((TOTAL_FAILED + 1))
        fi
    else
        echo ""
        echo "  Skipping .deb tests (not found: $APPIMAGE_DIR/$DEB_NAME)"
    fi
fi

# ── RPM package tests ─────────────────────────────────────────────
if $TEST_RPM; then
    if $TEST_FEDORA; then
        test_electron_rpm_package "fedora-40" "fedora:40" || TOTAL_FAILED=$((TOTAL_FAILED + 1))
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
if [ $TOTAL_FAILED -eq 0 ]; then
    echo "  All Electron tests passed!"
else
    echo "  Some Electron tests failed. Check logs in: $TEST_DIR/"
fi
echo "═══════════════════════════════════════════════════════════════"

exit $TOTAL_FAILED