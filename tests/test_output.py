from __future__ import annotations

import click
from click.testing import CliRunner
from rich.console import Console

from rs3tk.app import AppError
from rs3tk.output import cli_error, console

runner = CliRunner()


def test_console_is_rich_console() -> None:
    assert isinstance(console, Console)


def test_cli_error_catches_app_error() -> None:
    @click.command()
    @cli_error
    def cmd(ctx: click.Context) -> None:
        raise AppError("boom")

    result = runner.invoke(cmd)
    assert result.exit_code != 0
    assert "boom" in result.output


def test_cli_error_passes_through_other_exceptions() -> None:
    @click.command()
    @cli_error
    def cmd(ctx: click.Context) -> None:
        raise ValueError("not app error")

    result = runner.invoke(cmd)
    assert result.exit_code != 0
    assert isinstance(result.exception, ValueError)
    assert "not app error" in str(result.exception)


def test_cli_error_preserves_metadata() -> None:
    @cli_error
    def my_func(ctx: object) -> None:
        """My docstring."""
        pass

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "My docstring."
