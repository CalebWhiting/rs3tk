# rs3tk

Open-source Jagex Launcher replacement written in Python. **Linux only.**

A command-line tool to authenticate with your Jagex Account and launch
Old School RuneScape (Official, RuneLite, HDOS) or RuneScape 3.

## Features

- **Multiple clients** — Launch RS3, OSRS Official, RuneLite, or HDOS
- **Secure token storage** — Credentials stored in your OS keyring
- **Multi-account support** — Supports being logged into multiple Jagex accounts at once.
- **Browser login** — Login with in-built electron browser for a seamless experience, alternatively use the system browser.
- **Game status** — Check server status and latest news

## Installation

```bash
pip install .
```

For development:

```bash
pip install -e ".[dev]"
pre-commit install
```

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
rs3tk gui                     # graphical launcher (PySide6)
```

## Options

- `-v` / `--verbose` — Enable debug logging
- `-#` / `--censor` — Censor sensitive data (account IDs, etc.)

### play options

- `-c` / `--character` — Select a specific character
- `-i` / `--interactive` — Interactive mode
- `-f` / `--foreground` — Run client in foreground (show logs)
- `-n` / `--no-character` — Launch without JX_* env variables

## Supported Clients

| Client | Game |
|--------|------|
| RS3 NXT | RS3 |
| OSRS Official | OSRS |
| RuneLite | OSRS |
| HDOS | OSRS |

## Autoinstall

rs3tk can automatically download and install game clients:

```bash
# Install a client
rs3tk clients install runelite
rs3tk clients install rs3

# Remove a client
rs3tk clients remove runelite

# List installed clients
rs3tk clients list
```

Clients are installed to `~/.config/rs3tk/clients/{client}/` and include
self-updating launchers that check for new versions on each run.

## Configuration

Settings are stored at `~/.config/rs3tk/` and managed via the `config` command:

- `default_game` — `rs3` / `osrs` (used by `news` when `--game` is omitted)
- `default_client` — `rs3` / `official` / `runelite` / `hdos` (used by `play` interactive prompt and `clients set-default`)
- `default_character` — set via `accounts set-default NAME`
- `last_character` — auto-saved after `play` (used as fallback default)
- `locale` — `0`=en, `1`=de, `2`=fr, `3`=pt-br (RS3 news only)

OAuth tokens are stored in your OS keyring under the `rs3tk` service.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"
pre-commit install

# Run linter
ruff check src/

# Format code
ruff format src/

# Type check
mypy src/

# Run tests
pytest

# All of the above at once
ruff check src/ && ruff format --check src/ && mypy src/ && pytest
```

See `AGENTS.md` for the full structure, conventions, settings reference, and CLI command tree.

## Electron GUI (optional)

A separate Electron + React + TypeScript + Tailwind desktop app lives in
`electron/`. It talks to the Python `rs3tk-backend` HTTP server on
`http://127.0.0.1:8765`, so that must be running for it to work.

**Prerequisites:** Node.js 18+ and npm. The `electron/` directory
already has `node_modules/` checked into git, so no `npm install`
is required for a first run.

### Run in dev mode (with hot reload)

```bash
# Terminal 1 — start the Python backend on the default port
rs3tk-backend

# Terminal 2 — start the Electron app
cd electron
npm run dev
```

The renderer talks to the backend at `http://127.0.0.1:8765` by
default. If you change the port, update the corresponding setting in
the Electron app.

### Build a Linux AppImage

```bash
cd electron
npm run build:linux
# Output: electron/dist/RS3TK-{version}.AppImage
```

`build:unpack` produces a directory build (faster, no installer).
The Electron app reads from the same `~/.config/rs3tk/` directory as
the CLI, so login state is shared.

## License

MIT
