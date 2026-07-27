"""Test cli.py module."""

from __future__ import annotations

import rs3tk.cli as cli_module


class TestCLIBootstrap:
    def test_console_created(self) -> None:
        assert hasattr(cli_module, "console")
        assert cli_module.console is not None

    def test_censor_value(self) -> None:
        result = cli_module._censor_value("secret")
        assert result == "******"
        assert len(result) == 6

    def test_censor_value_empty(self) -> None:
        result = cli_module._censor_value("")
        assert result == ""


class TestCLICommands:
    def test_main_group_exists(self) -> None:
        assert cli_module.main is not None

    def test_auth_group_exists(self) -> None:
        assert cli_module.auth is not None

    def test_accounts_group_exists(self) -> None:
        assert cli_module.accounts is not None

    def test_clients_group_exists(self) -> None:
        assert cli_module.clients is not None

    def test_config_group_exists(self) -> None:
        assert cli_module.config is not None
