"""Client installer framework — installs self-updating Python launchers."""

from __future__ import annotations

import logging
import stat
from abc import ABC, abstractmethod
from pathlib import Path

from rs3tk.clients import CLIENTS_DIR

logger = logging.getLogger(__name__)
_DATA_DIR = Path(__file__).parent / "data"


class InstallError(Exception):
    pass


def _write_script(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


class ClientInstaller(ABC):
    @abstractmethod
    def install(self, target_dir: Path) -> Path:
        """Write launcher script to target_dir. Returns path to script."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if installation is possible (e.g., platform/dependencies)."""

    def _read_template(self, name: str) -> str:
        return (_DATA_DIR / name).read_text(encoding="utf-8")


class RuneLiteInstaller(ClientInstaller):
    def is_available(self) -> bool:
        return True

    def install(self, target_dir: Path) -> Path:
        script = target_dir / "runelite"
        _write_script(script, self._read_template("runelite.py"))
        return script


class HDOSInstaller(ClientInstaller):
    def is_available(self) -> bool:
        import shutil

        return shutil.which("java") is not None

    def install(self, target_dir: Path) -> Path:
        script = target_dir / "hdos"
        _write_script(script, self._read_template("hdos.py"))
        return script


class OfficialInstaller(ClientInstaller):
    def is_available(self) -> bool:
        import shutil

        return shutil.which("wine") is not None or shutil.which("umu-run") is not None

    def install(self, target_dir: Path) -> Path:
        script = target_dir / "osclient"
        _write_script(script, self._read_template("osclient.py"))
        return script


class RS3Installer(ClientInstaller):
    def is_available(self) -> bool:
        return True

    def install(self, target_dir: Path) -> Path:
        script = target_dir / "runescape"
        _write_script(script, self._read_template("rs3.py"))
        return script


INSTALLERS: dict[str, ClientInstaller] = {
    "official": OfficialInstaller(),
    "runelite": RuneLiteInstaller(),
    "hdos": HDOSInstaller(),
    "rs3": RS3Installer(),
}


def get_installer(client: str) -> ClientInstaller:
    key = client.lower()
    if key not in INSTALLERS:
        raise InstallError(f"No installer for: {client}. Available: {', '.join(INSTALLERS)}")
    return INSTALLERS[key]


def install_client(client: str) -> Path:
    """Install a launcher script to ~/.config/rs3tk/clients/{client}/. Returns script path."""
    installer = get_installer(client)
    if not installer.is_available():
        raise InstallError(f"{client} installer requirements not met")

    target_dir = CLIENTS_DIR / client
    target_dir.mkdir(parents=True, exist_ok=True)
    return installer.install(target_dir)
