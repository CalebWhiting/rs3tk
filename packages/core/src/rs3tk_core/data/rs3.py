#!/usr/bin/env python3
"""RuneScape 3 auto-update launcher for rs3tk.

Downloads the official Linux .deb package, extracts the client binary,
and bundles all shared library dependencies so the client runs without
any system-installed desktop packages.
"""

import argparse
import contextlib
import gzip
import io
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Literal

DEB_URL = "https://content.runescape.com/downloads/ubuntu/pool/non-free/r/runescape-launcher/runescape-launcher_2.2.12_amd64.deb"
PKG_INFO_URL = "https://content.runescape.com/downloads/ubuntu/dists/trusty/non-free/binary-amd64/Packages.gz"
USER_AGENT = "RS3-client/1.0"
_AR_HEADER_SIZE = 60
_AR_MAGIC = b"!<arch>"

# Supplemental dependencies needed by the NXT binary.
# The binary links against libraries that are missing or EOL on modern distros.
# All packages sourced from Ubuntu archive to guarantee ABI compatibility.
SUPPLEMENTAL_DEPS: list[dict[str, str]] = [
    # ── OpenSSL 1.1 (EOL, removed from noble) ──────────────────────
    {
        "name": "libssl1.1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb",
    },
    # ── GLib / GObject / GIO ──────────────────────────────────────
    {
        "name": "libglib2.0-0t64",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/g/glib2.0/libglib2.0-0t64_2.80.0-6ubuntu1_amd64.deb",
    },
    # ── X11 core ──────────────────────────────────────────────────
    {
        "name": "libx11-6",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libx11/libx11-6_1.8.7-1build1_amd64.deb",
    },
    {
        "name": "libbsd0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libb/libbsd/libbsd0_0.12.1-1build1_amd64.deb",
    },
    {
        "name": "libxext6",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxext/libxext6_1.3.4-1build2_amd64.deb",
    },
    {
        "name": "libxrender1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxrender/libxrender1_0.9.10-1.1build1_amd64.deb",
    },
    {
        "name": "libxfixes3",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxfixes/libxfixes3_6.0.0-2build1_amd64.deb",
    },
    {
        "name": "libxinerama1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxinerama/libxinerama1_1.1.4-3build1_amd64.deb",
    },
    {
        "name": "libxi6",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxi/libxi6_1.8.1-1build1_amd64.deb",
    },
    {
        "name": "libxrandr2",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxrandr/libxrandr2_1.5.2-2build1_amd64.deb",
    },
    {
        "name": "libxcursor1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxcursor/libxcursor1_1.2.1-1build1_amd64.deb",
    },
    {
        "name": "libxcomposite1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxcomposite/libxcomposite1_0.4.5-1build3_amd64.deb",
    },
    {
        "name": "libxdamage1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxdamage/libxdamage1_1.1.6-1build1_amd64.deb",
    },
    {
        "name": "libxxf86vm1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxxf86vm/libxxf86vm1_1.1.4-1build4_amd64.deb",
    },
    # ── XCB ───────────────────────────────────────────────────────
    {
        "name": "libxcb1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxcb/libxcb1_1.15-1ubuntu2_amd64.deb",
    },
    {
        "name": "libxcb-render0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxcb/libxcb-render0_1.15-1ubuntu2_amd64.deb",
    },
    {
        "name": "libxcb-shm0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxcb/libxcb-shm0_1.15-1ubuntu2_amd64.deb",
    },
    {
        "name": "libxau6",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxau/libxau6_1.0.9-1build6_amd64.deb",
    },
    {
        "name": "libxdmcp6",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libx/libxdmcp/libxdmcp6_1.1.3-0ubuntu6_amd64.deb",
    },
    # ── X11 session management ────────────────────────────────────
    {
        "name": "libice6",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libi/libice/libice6_1.0.10-1build3_amd64.deb",
    },
    {
        "name": "libsm6",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libs/libsm/libsm6_1.2.3-1build3_amd64.deb",
    },
    # ── GTK+ 2 (removed from noble; jammy package) ────────────────
    {
        "name": "libgtk2.0-0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/g/gtk+2.0/libgtk2.0-0_2.24.33-2ubuntu2_amd64.deb",
    },
    # ── GDK-Pixbuf ───────────────────────────────────────────────
    {
        "name": "libgdk-pixbuf-2.0-0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/g/gdk-pixbuf/libgdk-pixbuf-2.0-0_2.42.10+dfsg-3ubuntu3_amd64.deb",
    },
    # ── Pango / Cairo / Harfbuzz ──────────────────────────────────
    {
        "name": "libpango-1.0-0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/p/pango1.0/libpango-1.0-0_1.52.1+ds-1build1_amd64.deb",
    },
    {
        "name": "libpangoft2-1.0-0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/p/pango1.0/libpangoft2-1.0-0_1.52.1+ds-1build1_amd64.deb",
    },
    {
        "name": "libcairo2",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/c/cairo/libcairo2_1.18.0-3build1_amd64.deb",
    },
    {
        "name": "libpangocairo-1.0-0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/p/pango1.0/libpangocairo-1.0-0_1.52.1+ds-1build1_amd64.deb",
    },
    {
        "name": "libharfbuzz0b",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/h/harfbuzz/libharfbuzz0b_8.3.0-2build2_amd64.deb",
    },
    {
        "name": "libfribidi0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/f/fribidi/libfribidi0_1.0.13-3build1_amd64.deb",
    },
    {
        "name": "libthai0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libt/libthai/libthai0_0.1.29-2build1_amd64.deb",
    },
    {
        "name": "libdatrie1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libd/libdatrie/libdatrie1_0.2.13-3build1_amd64.deb",
    },
    {
        "name": "libgraphite2-3",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/g/graphite2/libgraphite2-3_1.3.14-2build1_amd64.deb",
    },
    # ── Font rendering ────────────────────────────────────────────
    {
        "name": "libfontconfig1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/f/fontconfig/libfontconfig1_2.15.0-1.1ubuntu2_amd64.deb",
    },
    {
        "name": "libfreetype6",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/f/freetype/libfreetype6_2.13.2+dfsg-1build3_amd64.deb",
    },
    {
        "name": "libpixman-1-0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/p/pixman/libpixman-1-0_0.42.2-1build1_amd64.deb",
    },
    # ── Image libraries ───────────────────────────────────────────
    {
        "name": "libpng16-16t64",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libp/libpng1.6/libpng16-16t64_1.6.43-5build1_amd64.deb",
    },
    {
        "name": "libjpeg-turbo8",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libj/libjpeg-turbo/libjpeg-turbo8_2.1.5-2ubuntu2_amd64.deb",
    },
    # ── ATK (accessibility) ──────────────────────────────────────
    {
        "name": "libatk1.0-0t64",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/a/at-spi2-core/libatk1.0-0t64_2.52.0-1build1_amd64.deb",
    },
    # ── OpenGL / EGL ──────────────────────────────────────────────
    {
        "name": "libegl1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libg/libglvnd/libegl1_1.7.0-1build1_amd64.deb",
    },
    {
        "name": "libopengl0",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libg/libglvnd/libopengl0_1.7.0-1build1_amd64.deb",
    },
    # ── Linux capabilities ────────────────────────────────────────
    {
        "name": "libcap2",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libc/libcap2/libcap2_2.66-5ubuntu2_amd64.deb",
    },
    # ── SELinux (transitive dep of libgio → libmount) ─────────────
    {
        "name": "libselinux1",
        "url": "http://archive.ubuntu.com/ubuntu/pool/main/libs/libselinux/libselinux1_3.9-4build1_amd64.deb",
    },
]


def fetch(url: str, progress: bool = False) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        total = int(r.headers.get("Content-Length", 0))
        data = bytearray()
        block_num = 0
        while True:
            chunk = r.read(65536)
            if not chunk:
                break
            data.extend(chunk)
            block_num += 1
            if progress and total > 0:
                downloaded = len(data)
                pct = min(100, downloaded * 100 // total)
                print(f"\r  {downloaded // 1024}/{total // 1024} KB ({pct}%)", end="", flush=True)
        if progress:
            print()
        return bytes(data)


def get_latest_version() -> str:
    raw = fetch(PKG_INFO_URL)
    text = gzip.decompress(raw).decode("utf-8")
    for line in text.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return ""


def _extract_data_tar(deb_data: bytes) -> tuple[bytes, str] | None:
    """Return (data_archive_bytes, compression_mode) from a .deb, or None."""
    if not deb_data.startswith(_AR_MAGIC):
        return None

    pos = 8
    while pos < len(deb_data) - _AR_HEADER_SIZE:
        header = deb_data[pos : pos + _AR_HEADER_SIZE]
        name = header[:16].decode("ascii").strip()
        size = int(header[48:58].decode("ascii").strip())
        pos += _AR_HEADER_SIZE

        if name in ("data.tar.xz", "data.tar.gz", "data.tar.bz2"):
            tar_modes: dict[str, Literal["r:xz", "r:gz", "r:bz2"]] = {
                "data.tar.xz": "r:xz",
                "data.tar.gz": "r:gz",
                "data.tar.bz2": "r:bz2",
            }
            return deb_data[pos : pos + size], tar_modes[name]

        if name == "data.tar.zst":
            return _decompress_zst(deb_data[pos : pos + size]), "r"

        pos += size
        if pos % 2 == 1:
            pos += 1

    return None


def _decompress_zst(data: bytes) -> bytes:
    """Decompress zstd data using the zstd CLI tool."""
    zstd = shutil.which("zstd") or shutil.which("unzstd")
    if not zstd:
        print(
            "Error: zstd is required to extract .deb packages but was not found.\nInstall with: sudo apt install zstd",
            file=sys.stderr,
        )
        sys.exit(1)

    proc = subprocess.run(
        [zstd, "-d", "--stdout"],
        input=data,
        capture_output=True,
        timeout=30,
    )
    if proc.returncode != 0:
        print(f"zstd decompression failed: {proc.stderr.decode(errors='replace')}", file=sys.stderr)
        sys.exit(1)
    return proc.stdout


def extract_binary_from_deb(deb_data: bytes) -> bytes | None:
    import tarfile

    result = _extract_data_tar(deb_data)
    if result is None:
        return None
    tar_data, mode = result

    with tarfile.open(fileobj=io.BytesIO(tar_data), mode=mode) as tf:  # type: ignore[call-overload]
        for member in tf.getmembers():
            if member.name == "./usr/share/games/runescape-launcher/runescape":
                f = tf.extractfile(member)
                if f:
                    return f.read()
    return None


def extract_libs_from_deb(deb_data: bytes, target_dir: Path) -> int:
    """Extract shared libraries (.so*) from a .deb archive into target_dir.

    Handles both regular files and symlinks. Returns the number of entries extracted.
    """
    import tarfile

    result = _extract_data_tar(deb_data)
    if result is None:
        return 0
    tar_data, mode = result
    count = 0

    target_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(tar_data), mode=mode) as tf:  # type: ignore[call-overload]
        for member in tf.getmembers():
            basename = os.path.basename(member.name)
            if basename.startswith("lib") and (".so" in basename or basename.endswith(".so")):
                dest = target_dir / basename
                if member.issym():
                    # Create the symlink
                    if not dest.exists():
                        os.symlink(member.linkname, dest)
                        count += 1
                elif member.isfile():
                    f = tf.extractfile(member)
                    if f:
                        dest.write_bytes(f.read())
                        count += 1
    return count


def extract_postinst_from_deb(deb_data: bytes) -> str | None:
    """Extract the postinst script from a .deb's control archive, if present."""
    import tarfile

    if not deb_data.startswith(_AR_MAGIC):
        return None

    pos = 8
    while pos < len(deb_data) - _AR_HEADER_SIZE:
        header = deb_data[pos : pos + _AR_HEADER_SIZE]
        name = header[:16].decode("ascii").strip()
        size = int(header[48:58].decode("ascii").strip())
        pos += _AR_HEADER_SIZE

        if name in ("control.tar.xz", "control.tar.gz", "control.tar.bz2"):
            tar_modes: dict[str, Literal["r:xz", "r:gz", "r:bz2"]] = {
                "control.tar.xz": "r:xz",
                "control.tar.gz": "r:gz",
                "control.tar.bz2": "r:bz2",
            }
            with tarfile.open(fileobj=io.BytesIO(deb_data[pos : pos + size]), mode=tar_modes[name]) as tf:  # type: ignore[call-overload]
                for member in tf.getmembers():
                    if os.path.basename(member.name) == "postinst":
                        f = tf.extractfile(member)
                        if f:
                            return f.read().decode("utf-8", errors="replace")
            break

        if name == "control.tar.zst":
            raw = _decompress_zst(deb_data[pos : pos + size])
            with tarfile.open(fileobj=io.BytesIO(raw), mode="r") as tf:
                for member in tf.getmembers():
                    if os.path.basename(member.name) == "postinst":
                        f = tf.extractfile(member)
                        if f:
                            return f.read().decode("utf-8", errors="replace")
            break

        pos += size
        if pos % 2 == 1:
            pos += 1

    return None


def apply_capabilities(binary: Path, postinst: str | None) -> None:
    """Apply file capabilities from the .deb's postinst script, if possible."""
    if postinst is None:
        return

    match = re.search(r"setcap\s+(\S+)\s+(\S+)", postinst)
    if not match:
        return

    caps = match.group(1)
    if shutil.which("setcap") is None:
        print(f"  Note: setcap not available; cannot apply capabilities ({caps})", file=sys.stderr)
        return

    with contextlib.suppress(subprocess.SubprocessError, OSError):
        subprocess.run(
            ["setcap", caps, str(binary)],
            capture_output=True,
            timeout=10,
        )


def install_supplemental_deps(lib_dir: Path) -> None:
    """Download and extract supplemental dependencies into lib_dir."""
    for dep in SUPPLEMENTAL_DEPS:
        marker = lib_dir / f".{dep['name']}"
        if marker.exists():
            continue

        print(f"  Downloading {dep['name']}...")
        deb_data = fetch(dep["url"], progress=True)
        extracted = extract_libs_from_deb(deb_data, lib_dir)
        del deb_data

        if extracted == 0:
            print(f"  Warning: no libraries found in {dep['name']} package", file=sys.stderr)
            continue

        marker.write_text(dep["url"])
        print(f"  {dep['name']} installed ({extracted} libraries)")


def check_system_deps(binary: Path, lib_dir: Path) -> list[str]:
    """Check for missing shared libraries using ldd.

    Returns a list of missing library names (human-readable).
    """
    env = os.environ.copy()
    bundled = str(lib_dir)
    if env.get("LD_LIBRARY_PATH"):
        env["LD_LIBRARY_PATH"] = f"{bundled}:{env['LD_LIBRARY_PATH']}"
    else:
        env["LD_LIBRARY_PATH"] = bundled

    try:
        result = subprocess.run(
            ["ldd", str(binary)],
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return []

    missing: list[str] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        # ldd format: "libfoo.so.1 => not found"
        if "=> not found" in line:
            lib_name = line.split()[0]
            missing.append(lib_name)

    return missing


def download_client(target: Path, version_file: Path, lib_dir: Path) -> None:
    version = get_latest_version()
    if not version:
        print("Could not determine latest RS3 version", file=sys.stderr)
        sys.exit(1)

    if target.exists() and version_file.exists() and version_file.read_text().strip() == version:
        print(f"RS3 {version} \u2014 up to date")
        return

    print(f"New version: {version}, downloading...")
    deb_data = fetch(DEB_URL, progress=True)

    # Extract the main client binary
    binary = extract_binary_from_deb(deb_data)
    if not binary:
        print("Failed to extract client from .deb package", file=sys.stderr)
        sys.exit(1)

    # Extract shared libraries from the .deb
    libs_extracted = extract_libs_from_deb(deb_data, lib_dir)

    # Extract and apply capabilities from postinst
    postinst = extract_postinst_from_deb(deb_data)
    del deb_data

    # Write the binary
    tmp = target.with_suffix(".tmp")
    tmp.write_bytes(binary)
    tmp.rename(target)
    target.chmod(0o755)
    apply_capabilities(target, postinst)

    # Install supplemental dependencies (OpenSSL 1.1, GTK2, etc.)
    install_supplemental_deps(lib_dir)

    version_file.write_text(version)
    print(f"RS3 {version} installed ({libs_extracted} bundled libraries)")


def main() -> None:
    parser = argparse.ArgumentParser(description="RuneScape 3 auto-update launcher")
    parser.add_argument("--install-only", action="store_true", help="Install/update without launching")
    args, remaining = parser.parse_known_args()

    script_dir = Path(__file__).resolve().parent
    binary = script_dir / "runescape-client"
    version_file = script_dir / ".version"
    lib_dir = script_dir / "lib"

    download_client(binary, version_file, lib_dir)

    if args.install_only:
        return

    # Check for missing libraries using ldd
    missing = check_system_deps(binary, lib_dir)
    if missing:
        unique = sorted(set(missing))
        print(
            f"Error: some bundled libraries could not be resolved: {', '.join(unique)}\n"
            f"This may indicate a packaging issue. Try re-running: rs3tk clients install rs3",
            file=sys.stderr,
        )
        sys.exit(1)

    env = os.environ.copy()

    # Prepend bundled libraries to LD_LIBRARY_PATH
    bundled = str(lib_dir)
    if env.get("LD_LIBRARY_PATH"):
        env["LD_LIBRARY_PATH"] = f"{bundled}:{env['LD_LIBRARY_PATH']}"
    else:
        env["LD_LIBRARY_PATH"] = bundled

    env["PULSE_PROP_OVERRIDE"] = "application.name='RuneScape' application.icon_name='runescape' media.role='game'"
    env["SDL_VIDEO_X11_WMCLASS"] = "RuneScape"
    env["PULSE_LATENCY_MSEC"] = "100"
    env.pop("XMODIFIERS", None)

    os.execve(str(binary), [str(binary), *remaining], env)


if __name__ == "__main__":
    main()
