# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for rs3tk-backend.

Builds a single-file executable from rs3tk.backend that bundles all
Python dependencies (httpx, pydantic, keyring, rich, click) so the
Electron AppImage can spawn it without a system Python.

Usage:
  PROJECT_ROOT=/path/to/rs3tk python -m PyInstaller rs3tk-backend.spec
"""

import os
from pathlib import Path

# Prefer the PROJECT_ROOT env var (set by build-backend.sh).
# Fall back to resolving relative to this spec file's location.
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", "")).resolve()
if not PROJECT_ROOT.exists():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

a = Analysis(
    [str(PROJECT_ROOT / "src" / "rs3tk" / "backend.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        (str(PROJECT_ROOT / "src" / "rs3tk" / "data"), "rs3tk/data"),
    ],
    hiddenimports=[
        "keyring.backends",
        "keyring.backends.SecretService",
        "keyring.backends.Keyring",
        "httpx._transports",
        "httpx._content",
        "httpx._decoders",
        "rs3tk.app",
        "rs3tk.clients",
        "rs3tk.config",
        "rs3tk.jagex_api",
        "rs3tk.rs_api",
        "rs3tk.game",
        "rs3tk.install",
        "rs3tk.output",
        "rs3tk.tables",
    ],
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
    name="rs3tk-backend",
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
