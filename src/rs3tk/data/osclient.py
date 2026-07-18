#!/usr/bin/env python3
"""OSRS Official client auto-update launcher for rs3tk.

Uses Jagex Direct6 CDN with piece-based download.
"""

import argparse
import base64
import gzip
import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path

DIRECT6_URL = "https://jagex.akamaized.net/direct6/"
META_PATH = "osrs-win"
USER_AGENT = "OSRS-client/1.0"
GZIP_HEADER_SKIP = 6


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        data: bytes = r.read()
        return data


def fetch_jwt(url: str) -> dict[str, object]:
    raw = fetch(url).decode("ascii").strip()
    b64 = raw.split(".")[1]
    pad = 4 - len(b64) % 4
    if pad != 4:
        b64 += "=" * pad
    result: dict[str, object] = json.loads(base64.urlsafe_b64decode(b64))
    return result


def download_client(target: Path, version_file: Path) -> None:
    metadata = fetch_jwt(f"{DIRECT6_URL}{META_PATH}/{META_PATH}.json")
    environments = metadata.get("environments", {})
    prod_env = environments.get("production", {}) if isinstance(environments, dict) else {}
    if isinstance(prod_env, dict):
        meta_id = str(prod_env.get("id", ""))
        version = str(prod_env.get("version", ""))
    else:
        meta_id = ""
        version = ""
    if not meta_id:
        print("Could not determine latest version", file=sys.stderr)
        sys.exit(1)

    if target.exists() and version_file.exists() and version_file.read_text().strip() == version:
        print(f"OSRS {version} \u2014 up to date")
        return

    print(f"New version: {version}, downloading...")

    catalog = fetch_jwt(f"{DIRECT6_URL}{META_PATH}/catalog/{meta_id}/catalog.json")
    metafile_url_raw = catalog.get("metafile") or catalog.get("metaFile")
    metafile_url = str(metafile_url_raw) if metafile_url_raw else ""
    if not metafile_url.startswith("http"):
        metafile_url = f"{DIRECT6_URL}{META_PATH}/{metafile_url.lstrip('/')}"

    metafile = fetch_jwt(metafile_url)
    files = metafile.get("files", [])
    exe_entry = None
    if isinstance(files, list):
        exe_entry = next((f for f in files if isinstance(f, dict) and str(f.get("name", "")).endswith(".exe")), None)
    if not exe_entry or not isinstance(exe_entry, dict):
        print("No executable found in metafile", file=sys.stderr)
        sys.exit(1)

    config = catalog.get("config", {})
    remote = config.get("remote", {}) if isinstance(config, dict) else {}
    base_url = str(remote.get("baseUrl", "")) if isinstance(remote, dict) else ""
    piece_format = str(remote.get("pieceFormat", "{TargetDigest}")) if isinstance(remote, dict) else "{TargetDigest}"

    pieces_raw = metafile.get("pieces", metafile.get("chunks", {}))
    if isinstance(pieces_raw, dict) and "digests" in pieces_raw:
        digests = list(pieces_raw["digests"])
    elif isinstance(pieces_raw, list):
        digests = list(pieces_raw)
    else:
        digests = []

    exe_offset = 0
    if isinstance(files, list):
        for file_entry in files:
            if isinstance(file_entry, dict) and str(file_entry.get("name", "")).endswith(".exe"):
                break
            exe_offset += int(file_entry.get("size", 0)) if isinstance(file_entry, dict) else 0

    assembled = b""
    for digest_entry in digests:
        digest_str = digest_entry.get("digest", "") if isinstance(digest_entry, dict) else str(digest_entry)
        if not digest_str or len(digest_str) < 2:
            continue
        try:
            hex_digest = base64.b64decode(digest_str).hex()
        except Exception:
            hex_digest = digest_str
        substituted = piece_format.replace("{SubString:0,2,{TargetDigest}}", hex_digest[:2])
        url = base_url + substituted.replace("{TargetDigest}", hex_digest)
        raw = fetch(url)
        try:
            assembled += gzip.decompress(raw[GZIP_HEADER_SKIP:])
        except Exception:
            assembled += raw

    exe_size = int(exe_entry.get("size", 0))
    exe_bytes = assembled[exe_offset : exe_offset + exe_size] if exe_size else assembled

    tmp = target.with_suffix(".exe.tmp")
    tmp.write_bytes(exe_bytes)
    tmp.rename(target)
    target.chmod(0o755)
    version_file.write_text(version)
    print(f"OSRS {version} installed")


def main() -> None:
    parser = argparse.ArgumentParser(description="OSRS Official client auto-update launcher")
    parser.add_argument("--install-only", action="store_true", help="Install/update without launching")
    args, remaining = parser.parse_known_args()

    script_dir = Path(__file__).resolve().parent
    exe = script_dir / "osclient.exe"
    version_file = script_dir / ".version"

    download_client(exe, version_file)

    if args.install_only:
        return

    wine = shutil.which("umu-run") or shutil.which("wine")
    if not wine:
        print("wine or umu-run not found in PATH", file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    env["WINEPREFIX"] = str(script_dir / "prefix")
    env["GAMEID"] = "1343370"
    env["PROTONPATH"] = "GE-Latest"
    env["PROTON_VERB"] = "runinprefix"

    os.execve(wine, [wine, str(exe), *remaining], env)


if __name__ == "__main__":
    main()
