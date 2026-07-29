"""Client installer framework — installs self-updating Python launchers."""

from __future__ import annotations

import logging
import shutil
import stat
from abc import ABC, abstractmethod
from pathlib import Path

from rs3tk_core.clients import CLIENTS_DIR

logger = logging.getLogger(__name__)
_DATA_DIR = Path(__file__).parent / "data"


class InstallError(Exception):
    pass


def _write_script(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


class ClientInstaller(ABC):
    script_name: str
    template_file: str

    def install(self, target_dir: Path) -> Path:
        target = target_dir / self.script_name
        content = (_DATA_DIR / self.template_file).read_text(encoding="utf-8")
        _write_script(target, content)
        return target

    @abstractmethod
    def is_available(self) -> bool:
        """Check if installation is possible (e.g., platform/dependencies)."""


class RuneLiteInstaller(ClientInstaller):
    script_name = "runelite"
    template_file = "runelite.py"

    def is_available(self) -> bool:
        return True


class HDOSInstaller(ClientInstaller):
    script_name = "hdos"
    template_file = "hdos.py"

    def is_available(self) -> bool:
        return shutil.which("java") is not None


class OfficialInstaller(ClientInstaller):
    script_name = "osclient"
    template_file = "osclient.py"

    def is_available(self) -> bool:
        return shutil.which("wine") is not None or shutil.which("umu-run") is not None


class RS3Installer(ClientInstaller):
    script_name = "runescape"
    template_file = "rs3.py"

    def is_available(self) -> bool:
        return True


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
