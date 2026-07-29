# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for rs3tk-bridge.

Builds a single-file executable from rs3tk_bridge that bundles all
Python dependencies (httpx, pydantic, keyring) so the Electron AppImage
can spawn it without a system Python.

Usage:
    bash scripts/build-bridge.sh
"""

import os
import sys
from pathlib import Path

# PyInstaller discovers the rs3tk_core install via the build venv that
# build-bridge.sh sets up. The data files (launcher templates) live in
# the rs3tk_core package's `data/` directory.
def _find_rs3tk_core_data() -> str:
    import rs3tk_core  # type: ignore[import-not-found]

    return os.path.join(os.path.dirname(rs3tk_core.__file__), "data")


datas = [
    (_find_rs3tk_core_data(), "rs3tk_core/data"),
]

hiddenimports = [
    "keyring.backends",
    "keyring.backends.SecretService",
    "keyring.backends.Keyring",
    "httpx._transports",
    "httpx._content",
    "httpx._decoders",
    "rs3tk_core",
    "rs3tk_core.app",
    "rs3tk_core.auth.session",
    "rs3tk_core.auth.browser",
    "rs3tk_core.auth.system_browser",
    "rs3tk_core.auth.oauth",
    "rs3tk_core.clients",
    "rs3tk_core.config",
    "rs3tk_core.jagex_api",
    "rs3tk_core.rs_api",
    "rs3tk_core.game",
    "rs3tk_core.install",
]

# PyInstaller first tries to interpret Analysis targets as filesystem
# paths. To make it import `rs3tk_bridge` as a module we need pathex to
# include the build venv's lib directory (where build-bridge.sh copied
# the bridge as `rs3tk_bridge/__init__.py`).
_VENV_LIB = Path(os.environ.get("RS3TK_BRIDGE_VENV_LIB", "")).resolve() if os.environ.get("RS3TK_BRIDGE_VENV_LIB") else None

if _VENV_LIB is None or not (_VENV_LIB / "rs3tk_bridge" / "__init__.py").exists():
    # Fallback: scan sys.path for an installed `rs3tk_bridge` (in case
    # the venv is at a different Python version than we expect).
    for p in sys.path:
        candidate = Path(p) / "rs3tk_bridge" / "__init__.py"
        if candidate.exists():
            _VENV_LIB = Path(p)
            break

if _VENV_LIB is None:
    raise RuntimeError(
        "rs3tk_bridge package not found. Set RS3TK_BRIDGE_VENV_LIB to the venv's "
        "site-packages directory, or run via build-bridge.sh which sets it."
    )

_BRIDGE_INIT = _VENV_LIB / "rs3tk_bridge" / "__init__.py"

a = Analysis(
    [str(_BRIDGE_INIT)],
    pathex=[str(_VENV_LIB)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6",
        "PyQt5",
        "PyQt6",
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "PIL",
        "cv2",
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="rs3tk-bridge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
