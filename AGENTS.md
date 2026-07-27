# AGENTS.md

## Project

rs3tk — Python CLI tool replacing the Jagex Launcher. Authenticates via OAuth2, manages game sessions, launches RS3/OSRS clients (Official, RuneLite, HDOS). Linux-only, Python 3.11+.

Three optional UIs ship alongside the CLI:
- **Terminal UI** (`rs3tk ui`) — Rich-based interactive menu
- **PySide6 GUI** (`rs3tk gui`) — Qt launcher with dark theme (extra: `pip install rs3tk[gui]`)
- **Electron GUI** (top-level `electron/`) — React + TypeScript + Tailwind app, talks to a local Python HTTP backend (`rs3tk-backend`)

> **Note on `electron/` directories:** two directories share this name for different purposes.
> - `src/rs3tk/auth/electron_login/` — a tiny headless Electron main-process script invoked by `auth/browser.py` to capture OAuth redirects.
> - top-level `electron/` — a full Electron + React + electron-vite + electron-builder GUI project with its own `package.json` and build pipeline.

## Commands

```bash
# Lint + format check + typecheck (run after every edit)
source .venv/bin/activate && ruff check src/ && ruff format --check src/ && mypy src/

# Auto-fix lint issues
ruff check --fix src/

# Auto-format
ruff format src/

# Run tests
pytest
```

## Structure

```
src/rs3tk/
  __init__.py          — __version__
  __main__.py          — python -m rs3tk entry
  cli.py               — Click commands (see "CLI command tree" below)
  app.py               — Shared CLI/UI logic (do_login, do_logout,
                         launch_game, do_autoinstall, get_news, …)
  config.py            — XDG paths, Settings model, keyring token storage
  jagex_api.py         — Pydantic models (Tokens, Character, GameSession,
                         UserProfile) + Jagex API calls
  rs_api.py            — RuneMetrics profile lookup
                         (RuneMetricsProfile, get_rune_metrics)
  game.py              — News + game status fetchers
  clients.py           — Config-driven game client launcher
                         (DEFAULT_CLIENTS, ConfigClient)
  install.py           — ABC installer framework
                         (RuneLiteInstaller, HDOSInstaller, …)
  output.py            — Rich console + @cli_error decorator
  tables.py            — Rich Table builders
  ui.py                — Rich interactive terminal UI (menu-driven)
  backend.py           — `rs3tk-backend` HTTP server backing the
                         Electron GUI
  data/                — Self-updating client launcher templates
                         (rs3.py, osclient.py, hdos.py, runelite.py)
  gui/                 — PySide6 Qt launcher (launcher_ui.py, demo.py,
                         assets/) — wired to `rs3tk gui`
  auth/
    session.py         — OAuth2 login flow, token storage/retrieval,
                         session creation
    browser.py         — Electron-based browser login (CDP-free Chromium)
    system_browser.py  — Manual URL paste fallback (--system-browser flag)
    oauth.py           — PKCE and state generation
    electron_login/    — Headless Electron main-process script that
                         captures OAuth redirects
../electron/           — Full Electron + React + TypeScript + Tailwind
                         GUI (own package.json, electron.vite config,
                         AppImage build via electron-builder)
tests/                 — pytest suite (mirrors src/rs3tk layout)
```

## Conventions

- Line length: 120
- Python 3.11 target
- ruff (E, F, I, N, UP, B, SIM, ANN) + mypy strict
- Module docstrings allowed; explanatory comments allowed where they document non-obvious external protocols (OAuth, JWT, JSONP, redirect handling)
- No emojis unless asked
- keyring for secrets, never in config files
- Pydantic for all API models
- httpx is **async** in `jagex_api.py` and `rs_api.py`; **sync** `httpx.get` is used in `game.py` and bridged to async callers via `app._run_sync`
- Click for CLI, Rich for output

## Settings

- `default_game` — `rs3` / `osrs` (used by `news` when `--game` omitted)
- `default_client` — `rs3` / `official` / `runelite` / `hdos` (used by `play` interactive prompt and `clients set-default`)
- `last_character` — auto-saved after `play`, used as fallback default in interactive prompt
- `default_character` — set via `accounts set-default NAME`, preferred default in `play` prompt
- `locale` — 0=en, 1=de, 2=fr, 3=pt-br (RS3 news only, OSRS always uses en)

## Membership check

`Character.is_member` (in `jagex_api.py`) checks two fields on each `Membership` entry:
1. `active_subscription: bool` — the Jagex API flag
2. `expires_at` (either `expiration_date` or `membership_expire`) — compared to `datetime.now()`

The Jagex API sometimes returns `active_subscription=False` even when the subscription is still valid. Falling back to the expiration date avoids false negatives. Always compare naive datetimes (strip tzinfo from the API string before comparing to `datetime.now()`).

## CLI command tree

- `auth {login, logout, list}` — OAuth login, logout, list stored accounts
- `accounts {list, set-default, unset-default}` — character-level operations
- `clients {list, install, remove, set-default}` — game client management
- `play [CLIENT] [-c CHAR] [-i] [-f] [-n]` — launch a game client
- `status` — game server status
- `news [-n N] [--game rs3|osrs]` — latest news
- `config {set}` — view/update settings
- `gui` — open PySide6 launcher
- `ui` — open Rich interactive terminal UI
