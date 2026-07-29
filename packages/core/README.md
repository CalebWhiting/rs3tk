# rs3tk-core

The core Python library. No UI, no HTTP, no Electron — just functions
that the CLI, the Rich TUI, and the Electron bridge all call into.

## Install

This is a workspace member of the rs3tk monorepo. From the monorepo root:

```bash
uv sync
```

## Public surface

The only public surface is `rs3tk_core.app` — see `app.py` for the
functions you can call. Everything else (`auth/`, `clients.py`,
`config.py`, `jagex_api.py`, `rs_api.py`, `install.py`, `game.py`) is
internal.

```python
from rs3tk_core.app import do_login, do_logout, launch_game
```
