# rs3tk

Open-source Jagex Launcher replacement for Linux. **Three modules, one
repo, one release tag.**

## What is this?

| Module                                     | What it is                                                                    | Install                       |
|--------------------------------------------|-------------------------------------------------------------------------------|-------------------------------|
| [`packages/core`](packages/core)           | The Python library. OAuth, Jagex API, RuneMetrics, game client management.    | `pip install rs3tk-core`      |
| [`packages/cli`](packages/cli)             | The `rs3tk` console script: Click CLI, Rich TUI.                              | `pip install rs3tk`           |
| [`packages/electron`](packages/electron)   | The Electron + React + TypeScript GUI as a downloadable AppImage.            | Download `RS3TK-*.AppImage`   |

The three modules share a single version (currently `1.0.0`) and a
single git tag. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for
how they fit together.

## Features

- **Multiple clients** — Launch RS3, OSRS Official, RuneLite, or HDOS
- **Secure token storage** — Credentials stored in your OS keyring
- **Multi-account support** — Be logged into multiple Jagex accounts at once
- **Three UIs** — Click CLI, Rich terminal UI, and Electron GUI
- **Game status + news** — Built-in, no browser needed

## Installation

### Python library + CLI (most users)

```bash
# Library only (for scripts)
pip install rs3tk-core

# CLI + TUI
pip install rs3tk
```

### Electron GUI

Download the latest `RS3TK-{version}.AppImage` from the
[Releases](../../releases) page. The AppImage bundles its own Python
via PyInstaller, so you don't need a system Python install.

## Usage

```bash
# Log in
rs3tk auth login
rs3tk auth list               # list stored accounts
rs3tk auth logout             # log out current account
rs3tk auth logout --all       # log out all accounts

# Manage characters
rs3tk accounts list
rs3tk accounts set-default "Cow31337Killer"
rs3tk accounts unset-default

# Launch a game
rs3tk play rs3               # RS3
rs3tk play official          # OSRS official
rs3tk play runelite          # RuneLite
rs3tk play hdos              # HDOS

# Interactive mode (pick client and character)
rs3tk play -i

# Launch with a specific character
rs3tk play runelite -c "Cow31337Killer"

# Launch without JX_* env variables (no character)
rs3tk play runelite -n

# Check game status
rs3tk status

# View latest news
rs3tk news
rs3tk news -n 10 --game rs3

# Settings
rs3tk config                  # show all settings
rs3tk config set --game osrs --client runelite
rs3tk config set --locale 2

# Game clients
rs3tk clients list
rs3tk clients install runelite
rs3tk clients remove runelite
rs3tk clients set-default runelite

# Alternate UIs
rs3tk ui                      # interactive terminal UI (Rich)
```

### Global flags

- `-v` / `--verbose` — Enable debug logging
- `-#` / `--censor` — Censor sensitive data (account IDs, etc.)

### `play` options

- `-c` / `--character` — Select a specific character
- `-i` / `--interactive` — Interactive mode
- `-f` / `--foreground` — Run client in foreground (show logs)
- `-n` / `--no-character` — Launch without JX_* env variables

## Supported clients

| Client        | Game |
|---------------|------|
| RS3 NXT       | RS3  |
| OSRS Official | OSRS |
| RuneLite      | OSRS |
| HDOS          | OSRS |

## Autoinstall

`rs3tk` can automatically download and install game clients:

```bash
rs3tk clients install runelite
rs3tk clients install rs3
rs3tk clients remove runelite
rs3tk clients list
```

Clients are installed to `~/.config/rs3tk/clients/{client}/` and
include self-updating launchers that check for new versions on each
run.

## Configuration

Settings are stored at `~/.config/rs3tk/` and managed via the
`config` command:

- `default_game` — `rs3` / `osrs` (used by `news` when `--game` is omitted)
- `default_client` — `rs3` / `official` / `runelite` / `hdos`
- `default_character` — set via `accounts set-default NAME`
- `last_character` — auto-saved after `play`
- `locale` — `0`=en, `1`=de, `2`=fr, `3`=pt-br (RS3 news only)

OAuth tokens are stored in your OS keyring under the `rs3tk` service.

## Development

```bash
# One-time setup (creates .venv, installs all Python + Node packages)
pnpm run setup-dev

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

# Build the AppImage
pnpm build:linux
```

See [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) for the full setup
guide and module structure.

## License

MIT
