# AGENTS.md

## Project

rs3tk — Python CLI tool replacing the Jagex Launcher. Authenticates via OAuth2, manages game sessions, launches RS3/OSRS clients (Official, RuneLite, HDOS). Linux-only, Python 3.11+.

## Commands

```bash
# Lint + format check + typecheck (run after every edit)
source .venv/bin/activate && ruff check src/ && ruff format --check src/ && mypy src/

# Auto-fix lint issues
ruff check --fix src/

# Auto-format
ruff format src/
```

## Structure

```
src/rs3tk/
  cli.py              — Click commands: login, logout, accounts, play, status, news, config, clients, ui
  config.py           — XDG paths, Settings model, keyring token storage
  jagex_api.py        — Pydantic models (Tokens, Character, GameSession, UserProfile) + API calls
  clients.py          — Config-driven game client launcher (DEFAULT_CLIENTS, ConfigClient)
  ui.py               — Rich interactive terminal UI (menu-driven)
  auth/
    session.py        — OAuth2 login flow, token storage/retrieval, session creation
    browser.py        — Electron-based browser login (CDP-free Chromium)
    system_browser.py — Manual URL paste fallback (--system-browser flag)
    oauth.py          — PKCE and state generation
    electron/main.js  — Electron preload script (intercepts redirects)
```

## Conventions

- Line length: 120
- Python 3.11 target
- ruff (E, F, I, N, UP, B, SIM, ANN) + mypy strict
- No comments unless asked
- No emojis unless asked
- keyring for secrets, never in config files
- Pydantic for all API models
- asyncio for httpx calls
- Click for CLI, Rich for output

## Settings

- `default_game` — rs3/osrs (used by `news` when `--game` omitted)
- `default_client` — official/runelite/hdos (used by `play` interactive prompt)
- `last_character` — auto-saved after `play`, used as default in interactive prompt
- `locale` — 0=en, 1=de, 2=fr, 3=pt-br (RS3 news only, OSRS always uses en)
