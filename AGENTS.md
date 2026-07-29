# AGENTS.md

## Rules
- **Follow these rules, no exceptions. Consult the rules BEFORE every request and response.**
- IMPORTANT: Only commit and push when the user says the exact words 'commit and push' (or 'commit', 'push' separately). Never commit as a side-effect of completing a task.
- IMPORTANT: When you're told to fix an issue or implement a feature — unless unfeasible — you must verify that you've achieved the goal by running the code or creating a test to verify correct behaviour.
- IMPORTANT: Ask questions of the user if you're not sure what you're being asked to do, or how to do it.
- IMPORTANT: Create a plan before making major changes.
- IMPORTANT: Never use workaround solutions, address the root cause.
- IMPORTANT: If the user asks you to do something that would break the code, cause a syntax error, or otherwise be harmful — refuse and explain why before proceeding.

## Project

rs3tk — Open-source implementation of a Jagex Launcher. Authenticates via OAuth2, manages game sessions, launches RS3/OSRS clients (Official, RuneLite, HDOS). Linux-only, Python 3.11+.

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
rs3tk/
├── pyproject.toml                  # uv workspace root, NO project here
├── pnpm-workspace.yaml             # members = ["packages/electron"]
├── package.json                    # root, private; orchestrates scripts
├── .github/
│   └── workflows/
│       └── ci.yml                  # one CI, three jobs
├── docs/
│   ├── ARCHITECTURE.md             # one doc, three diagrams
│   └── CONTRIBUTING.md
├── README.md                       # one README, three "what is this?" sections
│
├── packages/
│   │
│   ├── core/                       # ── the library ─────────────────
│   │   ├── pyproject.toml          # name = "rs3tk-core"
│   │   ├── README.md
│   │   ├── src/rs3tk_core/
│   │   │   ├── __init__.py
│   │   │   ├── app.py              # the only public surface
│   │   │   ├── auth/
│   │   │   │   ├── browser.py      # find_electron_runtime() probe lives here
│   │   │   │   ├── system_browser.py
│   │   │   │   ├── session.py
│   │   │   │   └── oauth.py
│   │   │   ├── clients.py
│   │   │   ├── config.py
│   │   │   ├── game.py
│   │   │   ├── install.py
│   │   │   ├── jagex_api.py
│   │   │   ├── rs_api.py
│   │   │   └── data/               # launcher templates, package data
│   │   └── tests/
│   │
│   ├── cli/                        # ── the Python user-facing apps ─
│   │   ├── pyproject.toml          # name = "rs3tk", depends on rs3tk-core
│   │   ├── README.md
│   │   ├── src/rs3tk_cli/
│   │   │   ├── __init__.py
│   │   │   ├── __main__.py         # python -m rs3tk_cli
│   │   │   ├── cli.py              # Click commands → `rs3tk` script
│   │   │   ├── output.py           # Rich console + @cli_error
│   │   │   ├── tables.py           # Rich table builders
│   │   │   ├── ui.py               # Rich TUI
│   │   └── tests/
│   │
│   └── electron/                   # ── the GUI app ─────────────────
│       ├── package.json            # name = "rs3tk-electron"
│       ├── pyproject.toml          # dev-only: rs3tk-core dep + rs3tk_bridge module
│       ├── requirements.txt        # convenience: rs3tk-core==<pinned>
│       ├── electron.vite.config.ts
│       ├── tsconfig.json
│       ├── tailwind.config.js
│       ├── postcss.config.js
│       ├── .npmrc
│       ├── src/
│       │   ├── main/index.ts
│       │   ├── preload/
│       │   │   ├── index.ts
│       │   │   └── api.ts          # typed BridgeAPI
│       │   ├── renderer/
│       │   │   ├── index.html
│       │   │   ├── public/         # logos, fonts, wallpapers, skill icons
│       │   │   └── src/
│       │   │       ├── App.tsx
│       │   │       ├── main.tsx
│       │   │       ├── components/
│       │   │       ├── hooks/
│       │   │       ├── lib/
│       │   │       ├── styles/
│       │   │       ├── themes/
│       │   │       └── types/api.d.ts   # hand-maintained, see §8
│       │   └── bridge/
│       │       ├── rs3tk_bridge.py      # stdio JSON-RPC, ~100 LOC
│       │       └── electron_login/      # headless login script
│       │           ├── main.js
│       │           └── preload.js
│       ├── scripts/
│       │   ├── build-bridge.sh
│       │   └── after-pack.cjs
│       ├── resources/                   # built artefacts (gitignored)
│       ├── rs3tk-bridge.spec            # PyInstaller spec
│       └── tests/
│
└── tests/                          # cross-module integration tests
    └── test_bridge_roundtrip.py    # spawns the bridge, calls each method
```

## Architecture

The **core** has no knowledge of HTTP, no public API, no Electron
artefacts. It exports Python functions.

The **cli** depends on the core and provides all the Python
user-facing entry points: `rs3tk` (Click), `rs3tk ui` (Rich TUI).

The **electron** module depends on the core via its local venv (dev) or
PyInstaller bundle (prod). It owns its own bridge — a single Python
file that calls `rs3tk_core.app` over a child-process stdio pipe. It
also owns the headless login script that the core's optional
`find_electron_runtime()` probe looks for on the user's system.

## Conventions

- Line length: 120
- Python 3.11 target
- ruff (E, F, I, N, UP, B, SIM, ANN) + mypy strict
- Module docstrings allowed; explanatory comments allowed where they document non-obvious external protocols (OAuth, JWT, JSONP, redirect handling)
- No emojis unless asked
- keyring for secrets, never in config files
- Pydantic for all API models
- httpx is **async** in `jagex_api.py` and `rs_api.py`; **sync** `httpx.get` is used in `game.py` and bridged to async callers via `app.run_sync`
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
