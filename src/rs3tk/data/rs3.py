#!/usr/bin/env python3
"""RuneScape 3 auto-update launcher for rs3tk.

Downloads the official Linux .deb package and extracts the client binary.
"""

import argparse
import gzip
import io
import os
import sys
import urllib.request
from pathlib import Path

DEB_URL = "https://content.runescape.com/downloads/ubuntu/pool/non-free/r/runescape-launcher/runescape-launcher_2.2.12_amd64.deb"
PKG_INFO_URL = "https://content.runescape.com/downloads/ubuntu/dists/trusty/non-free/binary-amd64/Packages.gz"
USER_AGENT = "RS3-client/1.0"
_AR_HEADER_SIZE = 60
_AR_MAGIC = b"!<arch>"


def fetch(url: str, progress: bool = False) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        total = int(r.headers.get("Content-Length", 0))
        data = b""
        block_num = 0
        while True:
            chunk = r.read(65536)
            if not chunk:
                break
            data += chunk
            block_num += 1
            if progress and total > 0:
                downloaded = len(data)
                pct = min(100, downloaded * 100 // total)
                print(f"\r  {downloaded // 1024}/{total // 1024} KB ({pct}%)", end="", flush=True)
        if progress:
            print()
        return data


def get_latest_version() -> str:
    raw = fetch(PKG_INFO_URL)
    text = gzip.decompress(raw).decode("utf-8")
    for line in text.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return ""


def extract_binary_from_deb(deb_data: bytes) -> bytes | None:
    import tarfile

    if not deb_data.startswith(_AR_MAGIC):
        return None

    data_offset = deb_data.find(b"\n")
    if data_offset == -1:
        return None

    pos = 8
    while pos < len(deb_data) - _AR_HEADER_SIZE:
        header = deb_data[pos : pos + _AR_HEADER_SIZE]
        name = header[:16].decode("ascii").strip()
        size = int(header[48:58].decode("ascii").strip())
        pos += _AR_HEADER_SIZE

        if name == "data.tar.xz" or name == "data.tar.gz" or name == "data.tar.bz2":
            tar_data = deb_data[pos : pos + size]
            mode = "xz" if name.endswith(".xz") else "gz" if name.endswith(".gz") else "bz2"
            with tarfile.open(fileobj=io.BytesIO(tar_data), mode=f"r:{mode}") as tf:
                for member in tf.getmembers():
                    if member.name == "./usr/share/games/runescape-launcher/runescape":
                        f = tf.extractfile(member)
                        if f:
                            return f.read()
            break

        pos += size
        if pos % 2 == 1:
            pos += 1

    return None


def download_client(target: Path, version_file: Path) -> None:
    version = get_latest_version()
    if not version:
        print("Could not determine latest RS3 version", file=sys.stderr)
        sys.exit(1)

    if target.exists() and version_file.exists() and version_file.read_text().strip() == version:
        print(f"RS3 {version} \u2014 up to date")
        return

    print(f"New version: {version}, downloading...")
    deb_data = fetch(DEB_URL, progress=True)

    binary = extract_binary_from_deb(deb_data)
    if not binary:
        print("Failed to extract client from .deb package", file=sys.stderr)
        sys.exit(1)

    tmp = target.with_suffix(".tmp")
    tmp.write_bytes(binary)
    tmp.rename(target)
    target.chmod(0o755)
    version_file.write_text(version)
    print(f"RS3 {version} installed")


def main() -> None:
    parser = argparse.ArgumentParser(description="RuneScape 3 auto-update launcher")
    parser.add_argument("--install-only", action="store_true", help="Install/update without launching")
    args, remaining = parser.parse_known_args()

    script_dir = Path(__file__).resolve().parent
    binary = script_dir / "runescape"
    version_file = script_dir / ".version"

    download_client(binary, version_file)

    if args.install_only:
        return

    env = os.environ.copy()
    env["PULSE_PROP_OVERRIDE"] = "application.name='RuneScape' application.icon_name='runescape' media.role='game'"
    env["SDL_VIDEO_X11_WMCLASS"] = "RuneScape"
    env["PULSE_LATENCY_MSEC"] = "100"
    env.pop("XMODIFIERS", None)

    os.execve(str(binary), [str(binary), *remaining], env)


if __name__ == "__main__":
    main()
