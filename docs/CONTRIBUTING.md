# Contributing

## Repo layout

```
rs3tk/
├── pyproject.toml                  # uv workspace root, no project here
├── pnpm-workspace.yaml             # members = ["packages/electron"]
├── package.json                    # root, private; orchestrates scripts
├── .github/workflows/              # CI + release
├── docs/                           # ARCHITECTURE.md, CONTRIBUTING.md
├── README.md
│
└── packages/
    ├── core/                       # rs3tk-core (Python library)
    ├── cli/                        # rs3tk (Python CLI + TUI)
    └── electron/                   # rs3tk-electron (Electron + React GUI)
```

## Tooling

- **uv** (Python package + workspace manager)
- **pnpm** (Node package manager for the electron module)
- **Python 3.11+** for the Python parts
- **Node 18+** for the electron module

## First-time setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install pnpm (or use your package manager)
sudo pacman -S pnpm          # Arch
sudo apt install npm && npm i -g pnpm   # Debian/Ubuntu

# Clone and enter the repo
git clone <repo-url> rs3tk
cd rs3tk

# One-shot setup: creates .venv, installs all Python + Node packages
pnpm run setup-dev
```

## Daily workflow

```bash
# Run all tests
pnpm test

# Run per-module tests
pnpm test:core
pnpm test:cli
pnpm test:bridge

# Lint + typecheck
pnpm lint
pnpm typecheck

# Run the Electron GUI in dev mode
pnpm dev:electron

# Build a Linux AppImage
pnpm build:linux
```

If you only want to work on one module:

```bash
# Python only
cd packages/core && ../../.venv/bin/python -m pytest tests
cd packages/cli  && ../../.venv/bin/python -m pytest tests

# Electron only
cd packages/electron && pnpm install && pnpm run dev
```

## Module responsibilities

### `packages/core` — the library

Pure Python. No UI, no HTTP, no Electron artefacts. The only public
surface is `rs3tk_core.app` — see `app.py` for the functions you can
call. Everything else (`auth/`, `clients.py`, `config.py`,
`jagex_api.py`, `rs_api.py`, `install.py`, `game.py`) is internal.

If you add a new feature to the core, you are adding a function
callable from the CLI, the TUI, and the Electron bridge.

### `packages/cli` — the user-facing Python apps

Depends on `rs3tk-core`. Provides:

- `rs3tk` — Click CLI (`cli.py`)
- `rs3tk ui` — Rich TUI (`ui.py`)

If you add a new CLI subcommand, edit `cli.py`. If you add a new
table layout, edit `tables.py`. If you add Rich-formatted output,
edit `output.py` (and import `console` from there).

### `packages/electron` — the GUI

Depends on `rs3tk-core` (in the dev venv) or the bundled `rs3tk-bridge`
binary (in the AppImage). Owns:

- `src/main/` — Electron main process (TypeScript)
- `src/preload/` — IPC bridge (TypeScript)
- `src/renderer/` — React UI (TypeScript + Tailwind)
- `src/bridge/rs3tk_bridge.py` — the Python bridge
- `src/bridge/electron_login/main.js` — the headless login script

If you add a new RPC method:
1. Add `@method("name")` to `rs3tk_bridge.py`.
2. Add the typed method to `BridgeAPI` in `src/preload/api.ts`.
3. Wire it up in `src/preload/index.ts`.
4. Use it in the renderer.

## Conventions

- Line length: 120
- Python 3.11 target
- ruff (E, F, I, N, UP, B, SIM, ANN) + mypy strict
- TypeScript strict
- Module docstrings allowed; explanatory comments allowed where they
  document non-obvious external protocols (OAuth, JWT, JSONP, redirect
  handling)
- No emojis
- keyring for secrets, never in config files
- Pydantic for all API models
- httpx is **async** in `jagex_api.py` and `rs_api.py`; **sync**
  `httpx.get` is used in `game.py` and bridged to async callers via
  `app.run_sync`
- Click for CLI, Rich for output
- React + Tailwind for the renderer

## CI

- `core` job: ruff check + format check + mypy + pytest (core)
- `cli` job: ruff check + format check + mypy + pytest (cli)
- `bridge` job: spawns the bridge as a subprocess and calls each
  method
- `electron` job: tsc + electron-vite build

See `.github/workflows/ci.yml`.

## Releasing

One tag, three packages, one release.

```bash
# Bump version in all four files
./scripts/bump-version.sh 1.5.0
git commit -am "v1.5.0"
git tag v1.5.0
git push --tags
```

The release workflow:
- Builds `rs3tk-core` and `rs3tk` sdist + wheel; publishes to PyPI.
- Builds the AppImage; attaches to the Codeberg Release.

## Adding a new dependency

- Python: add to the appropriate `packages/<x>/pyproject.toml`. For
  cross-cutting deps (used by both core and cli), put it in core.
- npm: add to `packages/electron/package.json`.

## Code of conduct

Be kind. Don't merge your own broken builds. Write tests for new
features. Update the docs if you make breaking changes.
