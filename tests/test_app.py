"""Test app.py — shared application logic for CLI and UI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rs3tk.app import (
    AppError,
    CharacterInfo,
    CharactersResult,
    _get_characters_result,
    check_game_status,
    do_autoinstall,
    do_login,
    do_logout,
    get_account_for_character,
    get_client_info,
    get_config,
    get_game_client,
    get_news,
    get_session_and_profile,
    launch_game,
    list_accounts,
    resolve_character,
    run_sync,
    set_default_character,
    unset_default_character,
    update_config,
)
from rs3tk.config import AccountInfo, Settings
from rs3tk.jagex_api import Character, UserProfile

# ── helpers ──────────────────────────────────────────────────────────────────


def _settings_with(accounts: list[AccountInfo] | None = None) -> Settings:
    return Settings(accounts=accounts or [])


def _user_profile(characters: list[Character] | None = None) -> UserProfile:
    return UserProfile(uuid="u", username="u", display_name="u", characters=characters or [])


async def _never_awaited() -> None:
    raise RuntimeError("should not be awaited")


# ── AppError ─────────────────────────────────────────────────────────────────


class TestAppError:
    def test_is_exception(self) -> None:
        assert issubclass(AppError, Exception)

    def test_can_be_raised_with_message(self) -> None:
        with pytest.raises(AppError, match="boom"):
            raise AppError("boom")


# ── run_sync ─────────────────────────────────────────────────────────────────


class TestRunSync:
    def test_returns_coroutine_result(self) -> None:
        async def coro() -> int:
            return 42

        assert run_sync(coro()) == 42

    def test_propagates_coroutine_exception(self) -> None:
        async def coro() -> None:
            raise ValueError("nope")

        with pytest.raises(ValueError, match="nope"):
            run_sync(coro())

    def test_raises_app_error_when_in_event_loop(self) -> None:
        import asyncio

        async def inner() -> None:
            with pytest.raises(AppError, match="Cannot call asyncio.run"):
                run_sync(_never_awaited())

        asyncio.run(inner())

    def test_raises_app_error_when_in_running_loop(self) -> None:
        import asyncio

        ran = False

        async def inner() -> None:
            nonlocal ran
            with pytest.raises(AppError, match="Cannot call asyncio.run"):
                run_sync(_never_awaited())
            ran = True

        asyncio.run(inner())
        assert ran


# ── CharacterInfo / CharactersResult ─────────────────────────────────────────


class TestCharacterInfo:
    def test_is_dataclass(self) -> None:
        char = CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=True)
        assert char.account_id == "a"
        assert char.display_name == "Alice"
        assert char.username == "u1"
        assert char.is_member is True


class TestCharactersResult:
    def test_construction(self) -> None:
        r = CharactersResult(characters=[], auth_errors=["oops"])
        assert r.characters == []
        assert r.auth_errors == ["oops"]


# ── do_login ─────────────────────────────────────────────────────────────────


class TestDoLogin:
    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    @patch("rs3tk.app.run_sync")
    def test_returns_username_and_count_for_new_account(
        self, mock_run: MagicMock, mock_load: MagicMock, _save: MagicMock
    ) -> None:
        mock_run.return_value = (MagicMock(), "newuser")
        mock_load.return_value = _settings_with(accounts=[])

        username, count = do_login()

        assert username == "newuser"
        assert count == 1

    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    @patch("rs3tk.app.run_sync")
    def test_does_not_duplicate_existing_account(
        self, mock_run: MagicMock, mock_load: MagicMock, mock_save: MagicMock
    ) -> None:
        mock_run.return_value = (MagicMock(), "existing")
        existing = _settings_with(accounts=[AccountInfo(username="existing")])
        mock_load.return_value = existing

        username, count = do_login()

        assert username == "existing"
        assert count == 1
        mock_save.assert_not_called()

    @patch("rs3tk.app.run_sync")
    def test_propagates_app_error(self, mock_run: MagicMock) -> None:
        # run_sync now raises AppError directly; do_login just lets it propagate.
        mock_run.side_effect = AppError("login failed")

        with pytest.raises(AppError, match="login failed"):
            do_login()


# ── do_logout ────────────────────────────────────────────────────────────────


class TestDoLogout:
    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    @patch("rs3tk.app.logout_account")
    def test_all_accounts_clears_everything(self, mock_lo: MagicMock, mock_load: MagicMock, _save: MagicMock) -> None:
        settings = _settings_with(accounts=[AccountInfo(username="u1"), AccountInfo(username="u2")])
        mock_load.return_value = settings

        do_logout(all_accounts=True)

        assert mock_lo.call_count == 2
        mock_lo.assert_any_call("u1")
        mock_lo.assert_any_call("u2")

    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    @patch("rs3tk.app.logout_account")
    def test_specific_user_removed(self, mock_lo: MagicMock, mock_load: MagicMock, mock_save: MagicMock) -> None:
        settings = _settings_with(accounts=[AccountInfo(username="u1"), AccountInfo(username="u2")])
        mock_load.return_value = settings

        do_logout("u1")

        mock_lo.assert_called_once_with("u1")
        saved: Settings = mock_save.call_args[0][0]
        assert [a.username for a in saved.accounts] == ["u2"]

    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    @patch("rs3tk.app.logout_account")
    def test_no_username_uses_first_account(
        self, mock_lo: MagicMock, mock_load: MagicMock, mock_save: MagicMock
    ) -> None:
        settings = _settings_with(accounts=[AccountInfo(username="u1")])
        mock_load.return_value = settings

        do_logout()

        mock_lo.assert_called_once_with("u1")

    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    @patch("rs3tk.app.logout_account")
    def test_no_username_and_no_accounts_is_noop(
        self, mock_lo: MagicMock, mock_load: MagicMock, mock_save: MagicMock
    ) -> None:
        mock_load.return_value = _settings_with(accounts=[])

        do_logout()

        mock_lo.assert_not_called()
        mock_save.assert_not_called()


# ── get_session_and_profile ──────────────────────────────────────────────────


class TestGetSessionAndProfile:
    @patch("rs3tk.app.run_sync")
    def test_returns_session_and_profile(self, mock_run: MagicMock) -> None:
        profile = _user_profile()
        mock_run.return_value = ("session-id", profile)

        sid, prof = get_session_and_profile("user1")

        assert sid == "session-id"
        assert prof is profile

    @patch("rs3tk.app.load_settings")
    def test_no_username_raises_when_no_accounts(self, mock_load: MagicMock) -> None:
        mock_load.return_value = _settings_with(accounts=[])

        with pytest.raises(AppError, match="Not logged in"):
            get_session_and_profile()

    @patch("rs3tk.app.load_settings")
    def test_no_username_uses_first_account(self, mock_load: MagicMock) -> None:
        settings = _settings_with(accounts=[AccountInfo(username="u1")])
        mock_load.return_value = settings

        with patch("rs3tk.app.run_sync", return_value=("sid", _user_profile())) as mock_run:
            sid, _ = get_session_and_profile()

        assert sid == "sid"
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0].__class__.__name__ == "coroutine"

    @patch("rs3tk.app.run_sync")
    def test_propagates_app_error(self, mock_run: MagicMock) -> None:
        # run_sync now raises AppError directly; get_session_and_profile just
        # lets it propagate.
        mock_run.side_effect = AppError("expired")

        with pytest.raises(AppError, match="expired"):
            get_session_and_profile("user1")


# ── _get_characters_result / get_all_characters ──────────────────────────────


class TestGetCharactersResult:
    @patch("rs3tk.app.load_settings")
    def test_no_accounts_returns_empty(self, mock_load: MagicMock) -> None:
        mock_load.return_value = _settings_with(accounts=[])

        result = _get_characters_result()

        assert result.characters == []
        assert result.auth_errors == []

    @patch("rs3tk.app.load_settings")
    def test_no_accounts_does_not_call_session(self, mock_load: MagicMock) -> None:
        mock_load.return_value = _settings_with(accounts=[])

        with patch("rs3tk.app.get_session") as mock_session:
            _get_characters_result()

        mock_session.assert_not_called()

    @patch("rs3tk.app.get_session")
    @patch("rs3tk.app.load_settings")
    def test_happy_path(self, mock_load: MagicMock, mock_session: MagicMock) -> None:
        settings = _settings_with(accounts=[AccountInfo(username="u1")])
        mock_load.return_value = settings

        async def fake_get_session(username: str) -> tuple[str, UserProfile]:
            return (
                "sid",
                _user_profile([Character(account_id="acc1", display_name="Alice")]),
            )

        mock_session.side_effect = fake_get_session

        result = _get_characters_result()

        assert len(result.characters) == 1
        assert result.characters[0].display_name == "Alice"
        assert result.characters[0].username == "u1"
        assert result.auth_errors == []

    @patch("rs3tk.app.get_session")
    @patch("rs3tk.app.load_settings")
    def test_records_auth_errors(self, mock_load: MagicMock, mock_session: MagicMock) -> None:
        settings = _settings_with(accounts=[AccountInfo(username="u1", display_name="FriendlyName")])
        mock_load.return_value = settings

        async def fake_get_session(username: str) -> tuple[str, UserProfile]:
            raise RuntimeError("expired for u1")

        mock_session.side_effect = fake_get_session

        result = _get_characters_result()

        assert result.characters == []
        assert len(result.auth_errors) == 1
        assert "FriendlyName" in result.auth_errors[0]

    @patch("rs3tk.app.get_session")
    @patch("rs3tk.app.load_settings")
    def test_records_other_exceptions(self, mock_load: MagicMock, mock_session: MagicMock) -> None:
        settings = _settings_with(accounts=[AccountInfo(username="u1")])
        mock_load.return_value = settings

        async def fake_get_session(username: str) -> tuple[str, UserProfile]:
            raise ConnectionError("network down")

        mock_session.side_effect = fake_get_session

        result = _get_characters_result()

        assert result.characters == []
        assert len(result.auth_errors) == 1
        assert "Failed to load profile" in result.auth_errors[0]


# ── get_account_for_character ────────────────────────────────────────────────


class TestGetAccountForCharacter:
    @patch("rs3tk.app.get_all_characters")
    def test_finds_character(self, mock_gac: MagicMock) -> None:
        mock_gac.return_value = [
            CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=False),
            CharacterInfo(account_id="b", display_name="Bob", username="u2", is_member=False),
        ]

        assert get_account_for_character("Bob") == "u2"
        assert get_account_for_character("alice") == "u1"  # case-insensitive

    @patch("rs3tk.app.get_all_characters")
    def test_returns_none_when_missing(self, mock_gac: MagicMock) -> None:
        mock_gac.return_value = [
            CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=False),
        ]

        assert get_account_for_character("Charlie") is None


# ── resolve_character ────────────────────────────────────────────────────────


class TestResolveCharacter:
    def test_finds_character(self) -> None:
        profile = _user_profile(
            [
                Character(account_id="acc1", display_name="Alice"),
                Character(account_id="acc2", display_name="Bob"),
            ]
        )

        acc_id, display = resolve_character("alice", profile)

        assert acc_id == "acc1"
        assert display == "Alice"

    def test_raises_app_error_when_missing(self) -> None:
        profile = _user_profile([Character(account_id="acc1", display_name="Alice")])

        with pytest.raises(AppError, match="Character 'Bob' not found"):
            resolve_character("Bob", profile)


# ── get_game_client ──────────────────────────────────────────────────────────


class TestGetGameClient:
    @patch("rs3tk.app.detect_client")
    def test_returns_client_when_installed(self, mock_detect: MagicMock) -> None:
        client = MagicMock()
        client.is_installed.return_value = True
        mock_detect.return_value = client

        assert get_game_client("runelite") is client

    @patch("rs3tk.app.detect_client")
    def test_raises_when_not_installed(self, mock_detect: MagicMock) -> None:
        client = MagicMock()
        client.is_installed.return_value = False
        client.name = "RuneLite"
        mock_detect.return_value = client

        with pytest.raises(AppError, match="RuneLite is not installed"):
            get_game_client("runelite")


# ── list_accounts ────────────────────────────────────────────────────────────


class TestListAccounts:
    @patch("rs3tk.app.load_settings")
    def test_returns_accounts_list(self, mock_load: MagicMock) -> None:
        accounts = [AccountInfo(username="u1"), AccountInfo(username="u2")]
        mock_load.return_value = _settings_with(accounts=accounts)

        assert list_accounts() == accounts


# ── default character ────────────────────────────────────────────────────────


class TestDefaultCharacter:
    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    def test_set(self, mock_load: MagicMock, mock_save: MagicMock) -> None:
        mock_load.return_value = _settings_with()

        set_default_character("Alice")

        saved: Settings = mock_save.call_args[0][0]
        assert saved.default_character == "Alice"

    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    def test_unset(self, mock_load: MagicMock, mock_save: MagicMock) -> None:
        mock_load.return_value = _settings_with()

        unset_default_character()

        saved: Settings = mock_save.call_args[0][0]
        assert saved.default_character is None


# ── check_game_status ────────────────────────────────────────────────────────


class TestCheckGameStatus:
    @patch("rs3tk.app.check_status")
    def test_returns_status_dict(self, mock_check: MagicMock) -> None:
        mock_check.return_value = {"playDisabled": False}

        assert check_game_status() == {"playDisabled": False}

    @patch("rs3tk.app.check_status")
    def test_wraps_game_error_in_app_error(self, mock_check: MagicMock) -> None:
        from rs3tk.game import GameError

        mock_check.side_effect = GameError("network")

        with pytest.raises(AppError, match="network"):
            check_game_status()


# ── get_news ─────────────────────────────────────────────────────────────────


class TestGetNews:
    @patch("rs3tk.app.fetch_news")
    @patch("rs3tk.app.load_settings")
    def test_uses_explicit_game(self, mock_load: MagicMock, mock_fetch: MagicMock) -> None:
        mock_load.return_value = _settings_with()
        mock_fetch.return_value = [{"title": "A"}]

        result = get_news(game="osrs", count=3)

        assert result == [{"title": "A"}]
        mock_fetch.assert_called_once_with("osrs", count=3, locale=0)

    @patch("rs3tk.app.fetch_news")
    @patch("rs3tk.app.load_settings")
    def test_uses_default_game_when_none(self, mock_load: MagicMock, mock_fetch: MagicMock) -> None:
        mock_load.return_value = Settings(default_game="osrs", default_client="official")
        mock_fetch.return_value = []

        get_news()

        mock_fetch.assert_called_once()
        args = mock_fetch.call_args.args
        assert args[0] == "osrs"

    @patch("rs3tk.app.fetch_news")
    @patch("rs3tk.app.load_settings")
    def test_uses_settings_locale_when_zero(self, mock_load: MagicMock, mock_fetch: MagicMock) -> None:
        mock_load.return_value = Settings(default_game="rs3", default_client="official", locale=2)
        mock_fetch.return_value = []

        get_news()

        kwargs = mock_fetch.call_args.kwargs
        assert kwargs["locale"] == 2

    @patch("rs3tk.app.fetch_news")
    @patch("rs3tk.app.load_settings")
    def test_explicit_zero_locale_falls_back_to_settings(self, mock_load: MagicMock, mock_fetch: MagicMock) -> None:
        # The current implementation uses `locale if locale else settings.locale`,
        # so an explicit 0 cannot be distinguished from the default-omitted case.
        # Document the actual behavior here; if distinguishing 0 becomes a
        # requirement, use a sentinel or split the parameter.
        mock_load.return_value = Settings(default_game="rs3", default_client="official", locale=2)
        mock_fetch.return_value = []

        get_news(locale=0)

        kwargs = mock_fetch.call_args.kwargs
        assert kwargs["locale"] == 2

    @patch("rs3tk.app.fetch_news")
    @patch("rs3tk.app.load_settings")
    def test_wraps_game_error(self, mock_load: MagicMock, mock_fetch: MagicMock) -> None:
        from rs3tk.game import GameError

        mock_load.return_value = _settings_with()
        mock_fetch.side_effect = GameError("news down")

        with pytest.raises(AppError, match="news down"):
            get_news()


# ── get_config / update_config ───────────────────────────────────────────────


class TestGetConfig:
    @patch("rs3tk.app.load_settings")
    def test_returns_settings(self, mock_load: MagicMock) -> None:
        settings = _settings_with()
        mock_load.return_value = settings

        assert get_config() is settings


class TestUpdateConfig:
    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    def test_no_changes_returns_false(self, mock_load: MagicMock, _save: MagicMock) -> None:
        mock_load.return_value = _settings_with()

        assert update_config() is False

    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    def test_any_change_returns_true_and_saves(self, mock_load: MagicMock, mock_save: MagicMock) -> None:
        mock_load.return_value = _settings_with()

        assert update_config(game="osrs") is True

        saved: Settings = mock_save.call_args[0][0]
        assert saved.default_game == "osrs"

    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    def test_sets_all_fields(self, mock_load: MagicMock, mock_save: MagicMock) -> None:
        mock_load.return_value = _settings_with()

        update_config(game="osrs", client="runelite", locale=3)

        saved: Settings = mock_save.call_args[0][0]
        assert saved.default_game == "osrs"
        assert saved.default_client == "runelite"
        assert saved.locale == 3


# ── get_client_info ──────────────────────────────────────────────────────────


class TestGetClientInfo:
    @patch("rs3tk.app.get_client_keys")
    @patch("rs3tk.app.detect_client")
    def test_returns_tuples_of_client_installed_path(self, mock_detect: MagicMock, mock_keys: MagicMock) -> None:
        mock_keys.return_value = ["runelite", "hdos"]
        c1 = MagicMock()
        c1.name = "RuneLite"
        c1.is_installed.return_value = True
        c1.executable.return_value = Path("/usr/bin/runelite")
        c2 = MagicMock()
        c2.name = "HDOS"
        c2.is_installed.return_value = False
        c2.executable.return_value = None
        mock_detect.side_effect = [c1, c2]

        result = get_client_info()

        assert len(result) == 2
        assert result[0] == (c1, True, "/usr/bin/runelite")
        assert result[1] == (c2, False, None)


# ── do_autoinstall ───────────────────────────────────────────────────────────


class TestDoAutoinstall:
    @patch("rs3tk.app.update_client_config")
    @patch("rs3tk.app.shutil.rmtree")
    @patch("rs3tk.app.CLIENTS_DIR")
    def test_remove_removes_dir_and_clears_config(
        self, mock_dir: MagicMock, mock_rm: MagicMock, mock_uc: MagicMock
    ) -> None:
        mock_dir.__truediv__.return_value.is_dir.return_value = True

        result = do_autoinstall("runelite", remove=True)

        assert "Removed runelite" in result
        mock_rm.assert_called_once()
        mock_uc.assert_called_once()

    @patch("rs3tk.app.update_client_config")
    @patch("rs3tk.app.subprocess.run")
    @patch("rs3tk.app.install_client")
    def test_install_happy_path(self, mock_install: MagicMock, mock_run: MagicMock, _mock_uc: MagicMock) -> None:
        mock_install.return_value = Path("/opt/rs3tk/runelite")
        proc = MagicMock()
        proc.returncode = 0
        proc.stdout = "installed"
        mock_run.return_value = proc

        result = do_autoinstall("runelite")

        assert "Installed runelite" in result
        mock_install.assert_called_once_with("runelite")

    @patch("rs3tk.app.install_client")
    def test_install_raises_on_install_error(self, mock_install: MagicMock) -> None:
        from rs3tk.install import InstallError

        mock_install.side_effect = InstallError("deps missing")

        with pytest.raises(AppError, match="deps missing"):
            do_autoinstall("runelite")

    @patch("rs3tk.app.subprocess.run")
    @patch("rs3tk.app.install_client")
    def test_install_raises_on_subprocess_failure(self, mock_install: MagicMock, mock_run: MagicMock) -> None:
        mock_install.return_value = Path("/opt/rs3tk/runelite")
        proc = MagicMock()
        proc.returncode = 1
        proc.stderr = "boom"
        mock_run.return_value = proc

        with pytest.raises(AppError, match="boom"):
            do_autoinstall("runelite")


# ── launch_game ──────────────────────────────────────────────────────────────


class TestLaunchGame:
    @patch("rs3tk.app.console")
    @patch("rs3tk.app.get_game_client")
    def test_no_character_path(self, mock_ggc: MagicMock, _console: MagicMock) -> None:
        client = MagicMock()
        client.name = "RuneLite"
        client.launch.return_value = MagicMock(pid=999)
        mock_ggc.return_value = client

        launch_game("runelite")

        client.launch.assert_called_once()
        args, _ = client.launch.call_args
        # First positional: session_id (empty when no character)
        assert args[0] == ""

    @patch("rs3tk.app.console")
    @patch("rs3tk.app.get_session_and_profile")
    @patch("rs3tk.app.get_account_for_character")
    @patch("rs3tk.app.save_settings")
    @patch("rs3tk.app.load_settings")
    @patch("rs3tk.app.get_game_client")
    def test_with_character_path_saves_last_character(
        self,
        mock_ggc: MagicMock,
        mock_load: MagicMock,
        mock_save: MagicMock,
        mock_gafc: MagicMock,
        mock_gsp: MagicMock,
        _console: MagicMock,
    ) -> None:
        client = MagicMock()
        client.name = "RuneLite"
        client.launch.return_value = MagicMock(pid=1)
        mock_ggc.return_value = client
        mock_gafc.return_value = "u1"
        mock_gsp.return_value = (
            "session-id",
            _user_profile([Character(account_id="acc1", display_name="Alice")]),
        )
        mock_load.return_value = _settings_with()

        launch_game("runelite", "Alice")

        client.launch.assert_called_once()
        saved: Settings = mock_save.call_args[0][0]
        assert saved.last_character == "Alice"

    @patch("rs3tk.app.get_account_for_character")
    @patch("rs3tk.app.get_game_client")
    def test_raises_when_character_not_in_any_account(self, mock_ggc: MagicMock, mock_gafc: MagicMock) -> None:
        mock_gafc.return_value = None

        with pytest.raises(AppError, match="not found in any stored account"):
            launch_game("runelite", "Ghost")

    @patch("rs3tk.app.console")
    @patch("rs3tk.app.get_game_client")
    def test_wraps_launch_errors(self, mock_ggc: MagicMock, _console: MagicMock) -> None:
        client = MagicMock()
        client.name = "RuneLite"
        client.launch.side_effect = FileNotFoundError("missing exe")
        mock_ggc.return_value = client

        with pytest.raises(AppError, match="missing exe"):
            launch_game("runelite")
