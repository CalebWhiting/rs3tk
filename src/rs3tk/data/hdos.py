#!/usr/bin/env python3
"""HDOS auto-update launcher for rs3tk."""

import argparse
import os
import shutil
import sys
import urllib.request
from pathlib import Path

HDOS_URL = "https://cdn.hdos.dev/launcher/latest/hdos-launcher.jar"


def get_etag() -> str:
    req = urllib.request.Request(HDOS_URL, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as r:
        etag = r.headers.get("ETag", "unknown")
        return str(etag) if etag else "unknown"


def _progress(block_num: int, block_size: int, total_size: int) -> None:
    downloaded = block_num * block_size
    if total_size > 0:
        pct = min(100, downloaded * 100 // total_size)
        print(f"\r  {downloaded // 1024}/{total_size // 1024} KB ({pct}%)", end="", flush=True)
    else:
        print(f"\r  {downloaded // 1024} KB", end="", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="HDOS auto-update launcher")
    parser.add_argument("--install-only", action="store_true", help="Install/update without launching")
    args, remaining = parser.parse_known_args()

    d = Path(__file__).resolve().parent
    jar = d / "hdos-launcher.jar"
    version_file = d / ".hdos.version"

    etag = get_etag()
    current = version_file.read_text().strip() if version_file.exists() else ""

    if current == etag and jar.exists():
        print("HDOS \u2014 up to date")
    else:
        print("Downloading HDOS...")
        tmp = jar.with_suffix(".tmp")
        urllib.request.urlretrieve(HDOS_URL, tmp, reporthook=_progress)
        print()
        tmp.rename(jar)
        version_file.write_text(etag)
        print("HDOS installed")

    if args.install_only:
        return

    java = shutil.which("java")
    if not java:
        print("Java not found in PATH", file=sys.stderr)
        sys.exit(1)

    os.execv(java, [java, "-jar", str(jar), *remaining])


if __name__ == "__main__":
    main()
