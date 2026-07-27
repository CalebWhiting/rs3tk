from __future__ import annotations

import functools
from collections.abc import Callable
from typing import TYPE_CHECKING

import click
from rich.console import Console

if TYPE_CHECKING:
    pass

console = Console()


def cli_error(func: Callable[..., object]) -> Callable[..., object]:
    @functools.wraps(func)
    @click.pass_context
    def wrapper(ctx: click.Context, /, *args: object, **kwargs: object) -> object:
        from rs3tk.app import AppError

        try:
            return func(ctx, *args, **kwargs)
        except AppError as e:
            raise click.ClickException(str(e)) from None

    return wrapper
