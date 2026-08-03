"""Test cli.py — Click command surface."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from rs3tk_core.app import AppError
from rs3tk_core.config import AccountInfo, Settings

from rs3tk_cli import cli
from rs3tk_cli.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# ── _censor_value / _find_default_char_index ─────────────────────────────────


class TestCensorValue:
    def test_replaces_with_stars(self) -> None:
        assert cli._censor_value("secret") == "******"

    def test_empty_string(self) -> None:
        assert cli._censor_value("") == ""


class TestFindDefaultCharIndex:
    def test_match_returns_index(self) -> None:
        from rs3tk_core.app import CharacterInfo

        chars = [
            CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=False),
            CharacterInfo(account_id="b", display_name="Bob", username="u2", is_member=False),
        ]
        assert cli._find_default_char_index(chars, "Bob") == 2

    def test_no_match_returns_none(self) -> None:
        from rs3tk_core.app import CharacterInfo

        chars = [CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=False)]
        assert cli._find_default_char_index(chars, "Ghost") is None

    def test_none_input_returns_none(self) -> None:
        assert cli._find_default_char_index([], None) is None


# ── pick_client / pick_character ─────────────────────────────────────────────


class TestPickClient:
    @patch("rs3tk_cli.cli.detect_client")
    @patch("rs3tk_cli.cli.get_client_keys")
    @patch("rs3tk_cli.cli.Prompt.ask")
    def test_returns_selected_key(self, mock_ask: MagicMock, mock_keys: MagicMock, mock_detect: MagicMock) -> None:
        mock_keys.return_value = ["runelite", "hdos"]
        mock_ask.return_value = "2"
        c1 = MagicMock()
        c1.name = "RuneLite"
        c1.is_installed.return_value = True
        c2 = MagicMock()
        c2.name = "HDOS"
        c2.is_installed.return_value = False
        mock_detect.side_effect = [c1, c2]

        settings = Settings(default_client="runelite")
        result = cli.pick_client(settings)

        assert result == "hdos"

    @patch("rs3tk_cli.cli.detect_client")
    @patch("rs3tk_cli.cli.get_client_keys")
    @patch("rs3tk_cli.cli.Prompt.ask")
    def test_uses_settings_default(self, mock_ask: MagicMock, mock_keys: MagicMock, mock_detect: MagicMock) -> None:
        mock_keys.return_value = ["runelite", "hdos"]
        mock_ask.return_value = "1"
        c1 = MagicMock()
        c1.name = "RuneLite"
        c1.is_installed.return_value = True
        c2 = MagicMock()
        c2.name = "HDOS"
        c2.is_installed.return_value = False
        mock_detect.side_effect = [c1, c2]

        settings = Settings(default_client="hdos")
        cli.pick_client(settings)

        assert mock_ask.call_args.kwargs["default"] == "2"


class TestPickCharacter:
    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one character"):
            cli.pick_character([], Settings())

    @patch("rs3tk_cli.cli.Prompt.ask")
    def test_returns_display_name(self, mock_ask: MagicMock) -> None:
        from rs3tk_core.app import CharacterInfo

        mock_ask.return_value = "2"
        chars = [
            CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=False),
            CharacterInfo(account_id="b", display_name="Bob", username="u2", is_member=False),
        ]

        result = cli.pick_character(chars, Settings())

        assert result == "Bob"

    @patch("rs3tk_cli.cli.Prompt.ask")
    def test_prefers_default_character_over_last(self, mock_ask: MagicMock) -> None:
        from rs3tk_core.app import CharacterInfo

        mock_ask.return_value = "1"
        chars = [CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=False)]
        settings = Settings(default_character="Alice", last_character="Bob")

        cli.pick_character(chars, settings)

        assert mock_ask.call_args.kwargs["default"] == "1"


# ── main group behavior ─────────────────────────────────────────────────────


class TestMainGroup:
    def test_version_flag(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "RS3TK" in result.output

    def test_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "RS3 ToolKit" in result.output


# ── auth ─────────────────────────────────────────────────────────────────────


class TestAuthLogin:
    @patch("rs3tk_cli.cli.do_login")
    def test_invokes_do_login(self, mock_do: MagicMock, runner: CliRunner) -> None:
        mock_do.return_value = ("testuser", 1)

        result = runner.invoke(main, ["auth", "login"])

        assert result.exit_code == 0
        mock_do.assert_called_once_with()

    @patch("rs3tk_cli.cli.do_login", side_effect=AppError("login failed"))
    def test_app_error_becomes_click_exception(self, _mock: MagicMock, runner: CliRunner) -> None:
        result = runner.invoke(main, ["auth", "login"])
        assert result.exit_code != 0
        assert "login failed" in result.output


class TestAuthLogout:
    @patch("rs3tk_cli.cli.do_logout")
    def test_invokes(self, mock_do: MagicMock, runner: CliRunner) -> None:
        result = runner.invoke(main, ["auth", "logout"])
        assert result.exit_code == 0
        mock_do.assert_called_once_with(None, all_accounts=False)

    @patch("rs3tk_cli.cli.do_logout")
    def test_all_flag(self, mock_do: MagicMock, runner: CliRunner) -> None:
        result = runner.invoke(main, ["auth", "logout", "--all"])
        assert result.exit_code == 0
        mock_do.assert_called_once_with(None, all_accounts=True)

    @patch("rs3tk_cli.cli.do_logout")
    def test_username_option(self, mock_do: MagicMock, runner: CliRunner) -> None:
        result = runner.invoke(main, ["auth", "logout", "-u", "alice"])
        assert result.exit_code == 0
        mock_do.assert_called_once_with("alice", all_accounts=False)


class TestAuthList:
    @patch("rs3tk_cli.cli.list_accounts")
    def test_no_accounts(self, mock_la: MagicMock, runner: CliRunner) -> None:
        mock_la.return_value = []
        result = runner.invoke(main, ["auth", "list"])
        assert result.exit_code == 0
        assert "No accounts found" in result.output

    @patch("rs3tk_cli.cli.list_accounts")
    def test_lists_accounts(self, mock_la: MagicMock, runner: CliRunner) -> None:
        mock_la.return_value = [AccountInfo(username="alice"), AccountInfo(username="bob")]
        result = runner.invoke(main, ["auth", "list"])
        assert result.exit_code == 0
        assert "alice" in result.output
        assert "bob" in result.output

    @patch("rs3tk_cli.cli.list_accounts")
    def test_censor(self, mock_la: MagicMock, runner: CliRunner) -> None:
        mock_la.return_value = [AccountInfo(username="alice")]
        result = runner.invoke(main, ["-#", "auth", "list"])
        assert result.exit_code == 0
        # The username should be censored, so it shouldn't appear in plain text
        assert "alice" not in result.output


# ── accounts ─────────────────────────────────────────────────────────────────


class TestAccountsGroup:
    def test_no_subcommand_invokes_list(self, runner: CliRunner) -> None:
        with patch("rs3tk_cli.cli.get_all_characters", return_value=[]):
            result = runner.invoke(main, ["accounts"])
        assert result.exit_code == 0
        assert "No characters found" in result.output

    def test_list_no_characters(self, runner: CliRunner) -> None:
        with patch("rs3tk_cli.cli.get_all_characters", return_value=[]):
            result = runner.invoke(main, ["accounts", "list"])
        assert result.exit_code == 0
        assert "No characters found" in result.output

    def test_list_with_characters(self, runner: CliRunner) -> None:
        from rs3tk_core.app import CharacterInfo

        chars = [CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=True)]
        with (
            patch("rs3tk_cli.cli.get_all_characters", return_value=chars),
            patch("rs3tk_cli.cli.load_settings", return_value=Settings()),
        ):
            result = runner.invoke(main, ["accounts", "list"])
        assert result.exit_code == 0
        assert "Alice" in result.output


class TestAccountsSetDefault:
    @patch("rs3tk_cli.cli.set_default_character")
    @patch("rs3tk_cli.cli.get_all_characters")
    def test_sets_default(self, mock_gac: MagicMock, mock_sd: MagicMock, runner: CliRunner) -> None:
        from rs3tk_core.app import CharacterInfo

        mock_gac.return_value = [
            CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=False),
        ]

        result = runner.invoke(main, ["accounts", "set-default", "alice"])

        assert result.exit_code == 0
        mock_sd.assert_called_once_with("alice")

    @patch("rs3tk_cli.cli.get_all_characters")
    def test_unknown_character_raises(self, mock_gac: MagicMock, runner: CliRunner) -> None:
        mock_gac.return_value = []

        result = runner.invoke(main, ["accounts", "set-default", "ghost"])

        assert result.exit_code != 0
        assert "not found" in result.output.lower()


class TestAccountsUnsetDefault:
    @patch("rs3tk_cli.cli.unset_default_character")
    @patch("rs3tk_cli.cli.load_settings")
    def test_clears_when_set(self, mock_load: MagicMock, mock_unset: MagicMock, runner: CliRunner) -> None:
        mock_load.return_value = Settings(default_character="alice")

        result = runner.invoke(main, ["accounts", "unset-default"])

        assert result.exit_code == 0
        mock_unset.assert_called_once()

    @patch("rs3tk_cli.cli.unset_default_character")
    @patch("rs3tk_cli.cli.load_settings")
    def test_noop_when_unset(self, mock_load: MagicMock, mock_unset: MagicMock, runner: CliRunner) -> None:
        mock_load.return_value = Settings(default_character=None)

        result = runner.invoke(main, ["accounts", "unset-default"])

        assert result.exit_code == 0
        mock_unset.assert_not_called()
        assert "No default character set" in result.output


# ── clients ──────────────────────────────────────────────────────────────────


class TestClientsGroup:
    def test_no_subcommand_invokes_list(self, runner: CliRunner) -> None:
        with patch("rs3tk_cli.cli.get_client_info", return_value=[]):
            result = runner.invoke(main, ["clients"])
        assert result.exit_code == 0


class TestClientsList:
    @patch("rs3tk_cli.cli.get_client_info")
    def test_invoke(self, mock_gci: MagicMock, runner: CliRunner) -> None:
        mock_gci.return_value = []
        result = runner.invoke(main, ["clients", "list"])
        assert result.exit_code == 0


class TestClientsInstall:
    @patch("rs3tk_cli.cli.do_autoinstall")
    def test_invokes(self, mock_do: MagicMock, runner: CliRunner) -> None:
        mock_do.return_value = "Installed"

        result = runner.invoke(main, ["clients", "install", "runelite"])

        assert result.exit_code == 0
        mock_do.assert_called_once_with("runelite")

    def test_unknown_client_rejected(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["clients", "install", "bogus"])
        assert result.exit_code != 0


class TestClientsRemove:
    @patch("rs3tk_cli.cli.do_autoinstall")
    def test_invokes_remove(self, mock_do: MagicMock, runner: CliRunner) -> None:
        mock_do.return_value = "Removed"

        result = runner.invoke(main, ["clients", "remove", "runelite"])

        assert result.exit_code == 0
        mock_do.assert_called_once_with("runelite", remove=True)


class TestClientsSetDefault:
    @patch("rs3tk_cli.cli.save_settings")
    @patch("rs3tk_cli.cli.load_settings")
    def test_sets_default(self, mock_load: MagicMock, mock_save: MagicMock, runner: CliRunner) -> None:
        mock_load.return_value = Settings()

        result = runner.invoke(main, ["clients", "set-default", "runelite"])

        assert result.exit_code == 0
        saved: Settings = mock_save.call_args[0][0]
        assert saved.default_client == "runelite"


# ── play ─────────────────────────────────────────────────────────────────────


class TestPlay:
    @patch("rs3tk_cli.cli.launch_game")
    @patch("rs3tk_cli.cli.get_all_characters")
    @patch("rs3tk_cli.cli.load_settings")
    def test_with_character_arg(
        self, mock_load: MagicMock, mock_gac: MagicMock, mock_lg: MagicMock, runner: CliRunner
    ) -> None:
        from rs3tk_core.app import CharacterInfo

        mock_load.return_value = Settings()
        mock_gac.return_value = [
            CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=False),
        ]

        result = runner.invoke(main, ["play", "runelite", "-c", "Alice"])

        assert result.exit_code == 0
        mock_lg.assert_called_once_with("runelite", "Alice", foreground=False)

    @patch("rs3tk_cli.cli.get_all_characters")
    @patch("rs3tk_cli.cli.load_settings")
    def test_no_character_no_login_raises(self, mock_load: MagicMock, mock_gac: MagicMock, runner: CliRunner) -> None:
        mock_load.return_value = Settings()
        mock_gac.return_value = []

        result = runner.invoke(main, ["play", "runelite"])

        assert result.exit_code != 0
        assert "Not logged in" in result.output

    @patch("rs3tk_core.app.get_game_client")
    @patch("rs3tk_cli.cli.load_settings")
    def test_no_character_flag(self, mock_load: MagicMock, mock_ggc: MagicMock, runner: CliRunner) -> None:
        mock_load.return_value = Settings()
        client = MagicMock()
        client.name = "RuneLite"
        client.launch.return_value = MagicMock(pid=42)
        mock_ggc.return_value = client

        result = runner.invoke(main, ["play", "runelite", "-n"])

        assert result.exit_code == 0
        client.launch.assert_called_once()

    @patch("rs3tk_cli.cli.pick_client")
    @patch("rs3tk_cli.cli.get_all_characters")
    @patch("rs3tk_cli.cli.load_settings")
    def test_no_client_arg_invokes_picker(
        self, mock_load: MagicMock, mock_gac: MagicMock, mock_pick: MagicMock, runner: CliRunner
    ) -> None:
        from rs3tk_core.app import CharacterInfo

        mock_load.return_value = Settings()
        mock_pick.return_value = "runelite"
        mock_gac.return_value = [
            CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=False),
        ]

        with patch("rs3tk_cli.cli.launch_game"):
            result = runner.invoke(main, ["play", "-c", "Alice"])

        assert result.exit_code == 0
        mock_pick.assert_called_once()


# ── status ───────────────────────────────────────────────────────────────────


class TestStatus:
    @patch("rs3tk_cli.cli.check_game_status")
    def test_all_operational(self, mock_check: MagicMock, runner: CliRunner) -> None:
        mock_check.return_value = {"playDisabled": False, "psaEnabled": False}

        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "All systems operational" in result.output

    @patch("rs3tk_cli.cli.check_game_status")
    def test_psa(self, mock_check: MagicMock, runner: CliRunner) -> None:
        mock_check.return_value = {
            "playDisabled": False,
            "psaEnabled": True,
            "psaMessage": "Down for maintenance",
        }

        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "PSA" in result.output
        assert "Down for maintenance" in result.output

    @patch("rs3tk_cli.cli.check_game_status")
    def test_offline(self, mock_check: MagicMock, runner: CliRunner) -> None:
        mock_check.return_value = {"playDisabled": True, "psaEnabled": False}

        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "offline" in result.output.lower()


# ── news ─────────────────────────────────────────────────────────────────────


class TestNews:
    @patch("rs3tk_cli.cli.get_news")
    def test_no_articles(self, mock_news: MagicMock, runner: CliRunner) -> None:
        mock_news.return_value = []

        result = runner.invoke(main, ["news"])

        assert result.exit_code == 0
        assert "No news found" in result.output

    @patch("rs3tk_cli.cli.get_news")
    def test_articles(self, mock_news: MagicMock, runner: CliRunner) -> None:
        mock_news.return_value = [{"title": "Update", "formattedDate": "2025-01-01"}]

        result = runner.invoke(main, ["news"])

        assert result.exit_code == 0
        assert "Update" in result.output

    @patch("rs3tk_cli.cli.get_news")
    @patch("rs3tk_cli.cli.load_settings")
    def test_default_game_used_when_not_specified(
        self, mock_load: MagicMock, mock_news: MagicMock, runner: CliRunner
    ) -> None:
        mock_load.return_value = Settings(default_game="osrs", default_client="official")
        mock_news.return_value = []

        runner.invoke(main, ["news"])

        mock_news.assert_called_once_with(game="osrs", count=5)

    @patch("rs3tk_cli.cli.get_news")
    def test_explicit_game_overrides_default(self, mock_news: MagicMock, runner: CliRunner) -> None:
        with patch("rs3tk_cli.cli.load_settings", return_value=Settings(default_game="osrs")):
            runner.invoke(main, ["news", "--game", "rs3", "-n", "3"])

        mock_news.assert_called_once_with(game="rs3", count=3)


# ── config ───────────────────────────────────────────────────────────────────


class TestConfigGroup:
    def test_no_subcommand_shows_settings(self, runner: CliRunner) -> None:
        with patch("rs3tk_cli.cli.get_config", return_value=Settings()):
            result = runner.invoke(main, ["config"])
        assert result.exit_code == 0
        assert "Settings" in result.output


class TestConfigSet:
    @patch("rs3tk_cli.cli.update_config")
    def test_change(self, mock_uc: MagicMock, runner: CliRunner) -> None:
        mock_uc.return_value = True

        result = runner.invoke(main, ["config", "set", "--game", "osrs"])

        assert result.exit_code == 0
        mock_uc.assert_called_once_with(game="osrs", client=None, locale=None)

    @patch("rs3tk_cli.cli.update_config")
    def test_no_change(self, mock_uc: MagicMock, runner: CliRunner) -> None:
        mock_uc.return_value = False

        result = runner.invoke(main, ["config", "set"])

        assert result.exit_code == 0
        assert "No changes" in result.output

    @patch("rs3tk_cli.cli.update_config")
    def test_all_options(self, mock_uc: MagicMock, runner: CliRunner) -> None:
        mock_uc.return_value = True

        result = runner.invoke(main, ["config", "set", "--game", "rs3", "--client", "runelite", "--locale", "2"])

        assert result.exit_code == 0
        mock_uc.assert_called_once_with(game="rs3", client="runelite", locale=2)


# ── ui (terminal UI launcher) ───────────────────────────────────────────────


class TestUiCommand:
    @patch("rs3tk_cli.ui.run_ui")
    def test_invokes_run_ui(self, mock_run: MagicMock, runner: CliRunner) -> None:
        result = runner.invoke(main, ["ui"])
        assert result.exit_code == 0
        mock_run.assert_called_once()
