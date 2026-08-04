from __future__ import annotations

import pytest
from rs3tk_core.install import InstallError, get_installer


def test_get_installer_official() -> None:
    installer = get_installer("official")
    assert installer.script_name == "osclient"


def test_get_installer_runelite() -> None:
    installer = get_installer("runelite")
    assert installer.script_name == "runelite"


def test_get_installer_hdos() -> None:
    installer = get_installer("hdos")
    assert installer.script_name == "hdos"


def test_get_installer_rs3() -> None:
    installer = get_installer("rs3")
    assert installer.script_name == "runescape"


def test_get_installer_unknown_raises() -> None:
    with pytest.raises(InstallError):
        get_installer("unknown")
