#!/usr/bin/env bash
# Test rs3tk packages in fresh containers.
#
# Usage:
#   ./scripts/test-packages.sh              # Test all packages
#   ./scripts/test-packages.sh --deb        # Test DEB only
#   ./scripts/test-packages.sh --rpm        # Test RPM only
#   ./scripts/test-packages.sh --apk        # Test APK only
#   ./scripts/test-packages.sh --arch       # Test Arch only
#   ./scripts/test-packages.sh --pip        # Test pip install only
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION=$(grep -oP '^version = "\K[^"]+' "$ROOT/packages/cli/pyproject.toml")
BUILD_DIR="$ROOT/build/packages"
TEST_DIR="$ROOT/build/test-results"
LOG_DIR="$TEST_DIR/logs"

# ── Parse arguments ────────────────────────────────────────────────
TEST_DEB=false
TEST_RPM=false
TEST_APK=false
TEST_ARCH=false
TEST_PIP=false
TEST_ALL=true

for arg in "$@"; do
    case "$arg" in
        --deb)   TEST_DEB=true; TEST_ALL=false ;;
        --rpm)   TEST_RPM=true; TEST_ALL=false ;;
        --apk)   TEST_APK=true; TEST_ALL=false ;;
        --arch)  TEST_ARCH=true; TEST_ALL=false ;;
        --pip)   TEST_PIP=true; TEST_ALL=false ;;
        *)       echo "Unknown flag: $arg"; exit 1 ;;
    esac
done

# If no specific format selected, test all
if ! $TEST_DEB && ! $TEST_RPM && ! $TEST_APK && ! $TEST_ARCH && ! $TEST_PIP; then
    TEST_DEB=true
    TEST_RPM=true
    TEST_APK=true
    TEST_ARCH=true
    TEST_PIP=true
fi

# ── Setup directories ──────────────────────────────────────────────
mkdir -p "$BUILD_DIR" "$LOG_DIR"

# ── Build wheels if needed ─────────────────────────────────────────
if [ ! -d "$BUILD_DIR/wheels" ] || [ -z "$(ls -A "$BUILD_DIR/wheels" 2>/dev/null)" ]; then
    echo "==> Building Python wheels..."
    cd "$ROOT"
    uv build --wheel --out-dir "$BUILD_DIR/wheels" packages/core/
    uv build --wheel --out-dir "$BUILD_DIR/wheels" packages/cli/
fi

# ── Test functions ─────────────────────────────────────────────────
test_deb() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Testing DEB packages"
    echo "═══════════════════════════════════════════════════════════════"
    
    local PASSED=0
    local FAILED=0
    
    # Test on Ubuntu 24.04
    echo ""
    echo "Testing on Ubuntu 24.04..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        ubuntu:24.04 \
        bash -c '
            set -euo pipefail
            export DEBIAN_FRONTEND=noninteractive
            
            # Install dependencies
            apt-get update && apt-get install -y --no-install-recommends \
                python3 python3-pip python3-httpx python3-pydantic \
                python3-keyring python3-click python3-rich
            
            # Install packages
            pip3 install --break-system-packages --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Ubuntu 24.04 test passed"
        ' > "$LOG_DIR/deb-ubuntu24.04.log" 2>&1; then
        echo "    ✓ Ubuntu 24.04"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ Ubuntu 24.04"
        echo "    Log: $LOG_DIR/deb-ubuntu24.04.log"
        FAILED=$((FAILED + 1))
    fi
    
    # Test on Debian 12
    echo ""
    echo "Testing on Debian 12..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        debian:12 \
        bash -c '
            set -euo pipefail
            export DEBIAN_FRONTEND=noninteractive
            
            # Install dependencies
            apt-get update && apt-get install -y --no-install-recommends \
                python3 python3-pip python3-httpx python3-pydantic \
                python3-keyring python3-click python3-rich
            
            # Install packages
            pip3 install --break-system-packages --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Debian 12 test passed"
        ' > "$LOG_DIR/deb-debian12.log" 2>&1; then
        echo "    ✓ Debian 12"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ Debian 12"
        echo "    Log: $LOG_DIR/deb-debian12.log"
        FAILED=$((FAILED + 1))
    fi
    
    # Test on Ubuntu 22.04 (NOTE: Has Python 3.10, rs3tk requires 3.11+)
    echo ""
    echo "Testing on Ubuntu 22.04 (expecting failure - Python 3.10)..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        ubuntu:22.04 \
        bash -c '
            set -euo pipefail
            export DEBIAN_FRONTEND=noninteractive
            
            # Install dependencies
            apt-get update && apt-get install -y --no-install-recommends \
                python3 python3-pip python3-httpx python3-pydantic \
                python3-keyring python3-click python3-rich
            
            # Install packages (Ubuntu 22.04 has older pip without --break-system-packages)
            pip3 install --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Ubuntu 22.04 test passed"
        ' > "$LOG_DIR/deb-ubuntu22.04.log" 2>&1; then
        echo "    ✓ Ubuntu 22.04"
        PASSED=$((PASSED + 1))
    else
        # Check if it failed due to Python version (expected)
        if grep -q "requires a different Python" "$LOG_DIR/deb-ubuntu22.04.log" 2>/dev/null; then
            echo "    ✓ Ubuntu 22.04 (correctly rejected - Python 3.10 < 3.11)"
            PASSED=$((PASSED + 1))
        else
            echo "    ✗ Ubuntu 22.04"
            echo "    Log: $LOG_DIR/deb-ubuntu22.04.log"
            FAILED=$((FAILED + 1))
        fi
    fi
    
    echo ""
    echo "DEB results: $PASSED passed, $FAILED failed"
    return $FAILED
}

test_rpm() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Testing RPM packages"
    echo "═══════════════════════════════════════════════════════════════"
    
    local PASSED=0
    local FAILED=0
    
    # Test on Fedora 40
    echo ""
    echo "Testing on Fedora 40..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        fedora:40 \
        bash -c '
            set -euo pipefail
            
            # Install dependencies
            dnf install -y python3 python3-pip python3-httpx python3-pydantic \
                python3-keyring python3-click python3-rich
            
            # Install packages
            pip3 install --break-system-packages --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Fedora 40 test passed"
        ' > "$LOG_DIR/rpm-fedora40.log" 2>&1; then
        echo "    ✓ Fedora 40"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ Fedora 40"
        echo "    Log: $LOG_DIR/rpm-fedora40.log"
        FAILED=$((FAILED + 1))
    fi
    
    # Test on Fedora 41
    echo ""
    echo "Testing on Fedora 41..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        fedora:41 \
        bash -c '
            set -euo pipefail
            
            # Install dependencies
            dnf install -y python3 python3-pip python3-httpx python3-pydantic \
                python3-keyring python3-click python3-rich
            
            # Install packages
            pip3 install --break-system-packages --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Fedora 41 test passed"
        ' > "$LOG_DIR/rpm-fedora41.log" 2>&1; then
        echo "    ✓ Fedora 41"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ Fedora 41"
        echo "    Log: $LOG_DIR/rpm-fedora41.log"
        FAILED=$((FAILED + 1))
    fi
    
    # Test on RHEL 9 (via AlmaLinux)
    echo ""
    echo "Testing on AlmaLinux 9 (RHEL-compatible)..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        almalinux:9 \
        bash -c '
            set -euo pipefail
            
            # Install dependencies
            dnf install -y python3 python3-pip python3-httpx python3-pydantic \
                python3-keyring python3-click python3-rich
            
            # Install packages
            pip3 install --break-system-packages --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "AlmaLinux 9 test passed"
        ' > "$LOG_DIR/rpm-almalinux9.log" 2>&1; then
        echo "    ✓ AlmaLinux 9"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ AlmaLinux 9"
        echo "    Log: $LOG_DIR/rpm-almalinux9.log"
        FAILED=$((FAILED + 1))
    fi
    
    echo ""
    echo "RPM results: $PASSED passed, $FAILED failed"
    return $FAILED
}

test_apk() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Testing APK packages"
    echo "═══════════════════════════════════════════════════════════════"
    
    local PASSED=0
    local FAILED=0
    
    # Test on Alpine 3.20
    echo ""
    echo "Testing on Alpine 3.20..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        alpine:3.20 \
        sh -c '
            set -euo pipefail
            
            # Install dependencies
            apk add --no-cache python3 py3-pip py3-httpx py3-pydantic \
                py3-keyring py3-click py3-rich
            
            # Install packages
            pip3 install --break-system-packages --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Alpine 3.20 test passed"
        ' > "$LOG_DIR/apk-alpine3.20.log" 2>&1; then
        echo "    ✓ Alpine 3.20"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ Alpine 3.20"
        echo "    Log: $LOG_DIR/apk-alpine3.20.log"
        FAILED=$((FAILED + 1))
    fi
    
    # Test on Alpine 3.19
    echo ""
    echo "Testing on Alpine 3.19..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        alpine:3.19 \
        sh -c '
            set -euo pipefail
            
            # Install dependencies
            apk add --no-cache python3 py3-pip py3-httpx py3-pydantic \
                py3-keyring py3-click py3-rich
            
            # Install packages
            pip3 install --break-system-packages --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Alpine 3.19 test passed"
        ' > "$LOG_DIR/apk-alpine3.19.log" 2>&1; then
        echo "    ✓ Alpine 3.19"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ Alpine 3.19"
        echo "    Log: $LOG_DIR/apk-alpine3.19.log"
        FAILED=$((FAILED + 1))
    fi
    
    echo ""
    echo "APK results: $PASSED passed, $FAILED failed"
    return $FAILED
}

test_arch() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Testing Arch Linux packages"
    echo "═══════════════════════════════════════════════════════════════"
    
    local PASSED=0
    local FAILED=0
    
    # Test on Arch Linux
    echo ""
    echo "Testing on Arch Linux..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        archlinux:latest \
        bash -c '
            set -euo pipefail
            
            # Install dependencies
            pacman -Sy --noconfirm python python-pip python-httpx python-pydantic \
                python-keyring python-click python-rich
            
            # Install packages
            pip3 install --break-system-packages --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Arch Linux test passed"
        ' > "$LOG_DIR/arch-archlinux.log" 2>&1; then
        echo "    ✓ Arch Linux"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ Arch Linux"
        echo "    Log: $LOG_DIR/arch-archlinux.log"
        FAILED=$((FAILED + 1))
    fi
    
    echo ""
    echo "Arch results: $PASSED passed, $FAILED failed"
    return $FAILED
}

test_pip() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Testing pip install"
    echo "═══════════════════════════════════════════════════════════════"
    
    local PASSED=0
    local FAILED=0
    
    # Test on Python 3.11 (minimum supported)
    echo ""
    echo "Testing on Python 3.11..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        python:3.11 \
        bash -c '
            set -euo pipefail
            
            # Install dependencies
            pip install httpx pydantic keyring click rich
            
            # Install packages
            pip install --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Python 3.11 test passed"
        ' > "$LOG_DIR/pip-python3.11.log" 2>&1; then
        echo "    ✓ Python 3.11"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ Python 3.11"
        echo "    Log: $LOG_DIR/pip-python3.11.log"
        FAILED=$((FAILED + 1))
    fi
    
    # Test on Python 3.12
    echo ""
    echo "Testing on Python 3.12..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        python:3.12 \
        bash -c '
            set -euo pipefail
            
            # Install dependencies
            pip install httpx pydantic keyring click rich
            
            # Install packages
            pip install --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Python 3.12 test passed"
        ' > "$LOG_DIR/pip-python3.12.log" 2>&1; then
        echo "    ✓ Python 3.12"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ Python 3.12"
        echo "    Log: $LOG_DIR/pip-python3.12.log"
        FAILED=$((FAILED + 1))
    fi
    
    # Test on Python 3.13
    echo ""
    echo "Testing on Python 3.13..."
    if docker run --rm --network=host \
        -v "$BUILD_DIR/wheels:/wheels:ro" \
        python:3.13 \
        bash -c '
            set -euo pipefail
            
            # Install dependencies
            pip install httpx pydantic keyring click rich
            
            # Install packages
            pip install --no-deps /wheels/*.whl
            
            # Test
            rs3tk --version
            echo "Python 3.13 test passed"
        ' > "$LOG_DIR/pip-python3.13.log" 2>&1; then
        echo "    ✓ Python 3.13"
        PASSED=$((PASSED + 1))
    else
        echo "    ✗ Python 3.13"
        echo "    Log: $LOG_DIR/pip-python3.13.log"
        FAILED=$((FAILED + 1))
    fi
    
    echo ""
    echo "pip results: $PASSED passed, $FAILED failed"
    return $FAILED
}

# ── Main execution ────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════════"
echo "  rs3tk Package Tester"
echo "  Version: $VERSION"
echo "═══════════════════════════════════════════════════════════════"

TOTAL_FAILED=0

if $TEST_DEB; then
    test_deb || TOTAL_FAILED=$((TOTAL_FAILED + $?))
fi

if $TEST_RPM; then
    test_rpm || TOTAL_FAILED=$((TOTAL_FAILED + $?))
fi

if $TEST_APK; then
    test_apk || TOTAL_FAILED=$((TOTAL_FAILED + $?))
fi

if $TEST_ARCH; then
    test_arch || TOTAL_FAILED=$((TOTAL_FAILED + $?))
fi

if $TEST_PIP; then
    test_pip || TOTAL_FAILED=$((TOTAL_FAILED + $?))
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
if [ $TOTAL_FAILED -eq 0 ]; then
    echo "  All tests passed!"
else
    echo "  Some tests failed. Check logs in: $LOG_DIR/"
fi
echo "═══════════════════════════════════════════════════════════════"

exit $TOTAL_FAILED