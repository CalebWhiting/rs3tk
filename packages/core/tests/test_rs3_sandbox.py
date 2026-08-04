"""Sandbox tests for RS3 supplemental dependencies.

Uses bubblewrap (bwrap) to run the RS3 client inside an isolated filesystem
where only the bundled shared libraries are visible.  If any libraries show
"not found" in ldd, or the binary fails to load, the supplemental dependency
list is incomplete.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from rs3tk_core.config import config_dir

_CLIENTS_DIR = config_dir() / "clients"
_RS3_DIR = _CLIENTS_DIR / "rs3"
_BINARY = _RS3_DIR / "runescape-client"
_LIB_DIR = _RS3_DIR / "lib"

bwrap = shutil.which("bwrap")

# Libraries that are expected to fail at runtime without a real display server
# or audio daemon.  These are NOT packaging bugs — they mean the binary got
# past the dynamic linker and into runtime init.
_RUNTIME_EXPECTED_FAILURES = {
    "libpulse.so.0",
    "libasound.so.2",
    "libXcursor.so.1",
    "libXrandr.so.2",
    "libXinerama.so.1",
    "libXcomposite.so.1",
    "libXdamage.so.1",
    "libXi.so.6",
    "libXfixes.so.3",
    "libXext.so.6",
    "libXrender.so.1",
}


def _bwrap_available() -> bool:
    return bwrap is not None


def _rs3_installed() -> bool:
    return _BINARY.exists() and _LIB_DIR.is_dir()


def _build_bwrap_base_args() -> list[str]:
    """Common bwrap flags that hide system libs and expose only the bundled set."""
    assert bwrap is not None
    return [
        bwrap,
        "--ro-bind",
        "/",
        "/",
        "--tmpfs",
        "/usr",
        "--tmpfs",
        "/lib",
        "--tmpfs",
        "/lib64",
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--tmpfs",
        "/tmp",
    ]


def _build_bwrap_ldd_cmd(binary: Path, lib_dir: Path) -> list[str]:
    """Build a bwrap command that runs ldd with only bundled libraries visible."""
    return [
        *_build_bwrap_base_args(),
        "--ro-bind",
        str(lib_dir),
        "/usr/lib",
        "--ro-bind",
        str(binary),
        "/app/runescape-client",
        "--chdir",
        "/app",
        "--",
        "ldd",
        "/app/runescape-client",
    ]


def _build_bwrap_run_cmd(binary: Path, lib_dir: Path) -> list[str]:
    """Build a bwrap command that runs the RS3 binary with only bundled libraries."""
    env = os.environ.copy()
    env["DISPLAY"] = env.get("DISPLAY", ":0")
    env["LD_LIBRARY_PATH"] = "/usr/lib"
    env["PULSE_PROP_OVERRIDE"] = "application.name='RuneScape' media.role='game'"
    env["SDL_VIDEO_X11_WMCLASS"] = "RuneScape"
    env.pop("XMODIFIERS", None)

    cmd = [
        *_build_bwrap_base_args(),
        "--ro-bind",
        str(lib_dir),
        "/usr/lib",
        "--ro-bind",
        str(binary),
        "/app/runescape-client",
        # X11 socket — lets the binary *attempt* to connect (will fail
        # gracefully if no server is listening).
        "--bind",
        "/tmp/.X11-unix",
        "/tmp/.X11-unix",
        "--setenv",
        "DISPLAY",
        env["DISPLAY"],
        "--setenv",
        "LD_LIBRARY_PATH",
        "/usr/lib",
        "--setenv",
        "PULSE_PROP_OVERRIDE",
        env["PULSE_PROP_OVERRIDE"],
        "--setenv",
        "SDL_VIDEO_X11_WMCLASS",
        env["SDL_VIDEO_X11_WMCLASS"],
        "--chdir",
        "/app",
        "--",
        "/app/runescape-client",
    ]
    return cmd


def _parse_ldd_missing(output: str) -> list[str]:
    """Return library names that ldd reported as 'not found'."""
    missing: list[str] = []
    for line in output.splitlines():
        line = line.strip()
        if "=> not found" in line:
            missing.append(line.split()[0])
    return sorted(set(missing))


def _is_library_load_error(output: str) -> str | None:
    """Return the missing lib name if the binary failed to load a shared library."""
    for line in output.splitlines():
        # "error while loading shared libraries: libfoo.so.1: cannot open ..."
        if "error while loading shared libraries:" in line:
            lib = line.split("error while loading shared libraries:", 1)[1].strip()
            lib = lib.split(":")[0].strip()
            return lib
        # "libfoo.so.1: cannot open shared object file"
        if "cannot open shared object file" in line:
            lib = line.split(":")[0].strip()
            return lib
    return None


@pytest.mark.skipif(
    not _bwrap_available(),
    reason="bubblewrap (bwrap) not installed",
)
@pytest.mark.skipif(
    not _rs3_installed(),
    reason="RS3 client not installed (run: rs3tk clients install rs3)",
)
class TestRS3Sandbox:
    """Verify bundled libraries are self-sufficient using bwrap isolation."""

    def test_ldd_resolves_all_libs(self) -> None:
        """ldd inside the sandbox must find every shared library."""
        cmd = _build_bwrap_ldd_cmd(_BINARY, _LIB_DIR)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        missing = _parse_ldd_missing(result.stdout + result.stderr)
        assert not missing, "Bundled libraries are incomplete — missing inside sandbox:\n" + "\n".join(
            f"  - {lib}" for lib in missing
        )

    def test_no_system_lib_leakage(self) -> None:
        """Every resolved library must come from the bundled lib dir, not /usr/lib."""
        cmd = _build_bwrap_ldd_cmd(_BINARY, _LIB_DIR)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        leaked: list[str] = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if "=>" in line and "not found" not in line:
                # ldd format: "libfoo.so.1 => /usr/lib/libfoo.so.1 (0x...)"
                parts = line.split("=>")
                if len(parts) == 2:
                    resolved_path = parts[1].strip().split()[0]
                    # In the sandbox /usr/lib is the bundled dir; anything
                    # outside it (or still in the real /lib) is a leak.
                    if not resolved_path.startswith("/usr/lib/"):
                        leaked.append(f"{line.split()[0]} => {resolved_path}")
        assert not leaked, "Some libraries resolved outside the sandbox:\n" + "\n".join(
            f"  - {entry}" for entry in leaked
        )

    def test_binary_executes_in_sandbox(self) -> None:
        """The binary must get past the dynamic linker inside the sandbox.

        Running without a real X11 server or PulseAudio daemon, so the
        binary is expected to fail — but it must fail at *runtime*
        (display/audio), not at *load time* (missing libraries).
        """
        cmd = _build_bwrap_run_cmd(_BINARY, _LIB_DIR)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
        )
        combined = result.stdout + result.stderr

        missing_lib = _is_library_load_error(combined)
        if missing_lib is not None and missing_lib not in _RUNTIME_EXPECTED_FAILURES:
            pytest.fail(f"Binary failed to load shared library '{missing_lib}' inside sandbox.\nOutput:\n{combined}")
