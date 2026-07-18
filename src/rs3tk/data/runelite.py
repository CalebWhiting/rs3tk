#!/usr/bin/env python3
"""RuneLite auto-update launcher for rs3tk."""

import argparse
import json
import os
import stat
import urllib.request
from pathlib import Path

GITHUB_API = "https://api.github.com/repos/runelite/launcher/releases/latest"
DL_URL = "https://github.com/runelite/launcher/releases/latest/download/RuneLite.AppImage"


def get_latest_tag() -> str:
    req = urllib.request.Request(GITHUB_API, headers={"Accept": "application/vnd.github.v3+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data: dict[str, object] = json.loads(r.read())
        tag = data.get("tag_name", "unknown")
        return str(tag) if tag else "unknown"


def _progress(block_num: int, block_size: int, total_size: int) -> None:
    downloaded = block_num * block_size
    if total_size > 0:
        pct = min(100, downloaded * 100 // total_size)
        print(f"\r  {downloaded // 1024}/{total_size // 1024} KB ({pct}%)", end="", flush=True)
    else:
        print(f"\r  {downloaded // 1024} KB", end="", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="RuneLite auto-update launcher")
    parser.add_argument("--install-only", action="store_true", help="Install/update without launching")
    args, remaining = parser.parse_known_args()

    d = Path(__file__).resolve().parent
    appimage = d / "RuneLite.AppImage"
    hash_file = d / ".runelite.sha256"

    latest = get_latest_tag()
    current = hash_file.read_text().strip() if hash_file.exists() else ""

    if appimage.exists() and os.access(appimage, os.X_OK) and current == latest:
        print(f"RuneLite {latest} \u2014 up to date")
    else:
        print(f"Downloading RuneLite {latest}...")
        tmp = appimage.with_suffix(".tmp")
        urllib.request.urlretrieve(DL_URL, tmp, reporthook=_progress)
        print()
        tmp.chmod(tmp.stat().st_mode | stat.S_IEXEC)
        tmp.rename(appimage)
        hash_file.write_text(latest)
        print(f"RuneLite {latest} installed")

    if args.install_only:
        return

    os.execv(str(appimage), [str(appimage), *remaining])


if __name__ == "__main__":
    main()
