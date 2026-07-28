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
`electron/`. It spawns the Python `rs3tk-backend` HTTP server itself on
`http://127.0.0.1:8765` at startup, so no separate backend process is
required for normal use.

**Prerequisites:** Node.js 18+ and a system `python3` (the GUI will
auto-create a venv and install `rs3tk` into it on first run if no
existing install is found). Works on PEP 658 systems (Kali, Fedora,
etc.) where `pip install` is blocked for the system Python.

### Quick start

```bash
cd electron && npm install && npm run dev
```

That's it. On first run the GUI will create a venv at
`~/.config/rs3tk/venv` and `pip install rs3tk` into it (takes a minute
on first run; instant thereafter). The window opens once setup
completes.

If the system has no `python3` (rare), install it first. If the venv
setup fails for any reason, the GUI shows an error dialog with the
underlying error.

### How the backend is located

The GUI checks, in order:
1. Is port 8765 already in use? (yes → done)
2. Project-local `.venv` with `rs3tk` importable
3. `rs3tk-backend` on `$PATH`
4. System `python3` with `rs3tk` importable
5. None of the above → auto-create `~/.config/rs3tk/venv` + install

In dev (running from a checkout) the project `.venv` is preferred.
In production the user venv is the canonical location.

### Run in dev mode (with hot reload)

```bash
cd electron
npm run dev
```

The Electron main process will locate the backend (vending-venv first,
then `rs3tk-backend` on `$PATH`, then `python3 -m rs3tk.backend`) and
spawn it on port 8765. The renderer connects to the same URL.

To run the backend separately for debugging, start it in another
terminal first:

```bash
rs3tk-backend   # listens on 127.0.0.1:8765
```

The Electron app detects that the port is already in use and skips
spawning its own copy.

### Build a Linux AppImage

```bash
cd electron
npm run build:linux
# Output: electron/dist/RS3TK-{version}.AppImage
```

`npm run build:linux` does three things:
1. Runs `scripts/build-backend.sh` which creates a standalone `rs3tk-backend`
   binary via PyInstaller (bundled Python + all deps, no system Python needed)
2. Builds the Electron app with `electron-vite`
3. Packages everything into an AppImage

`build:unpack` produces a directory build (faster, no installer).
The Electron app reads from the same `~/.config/rs3tk/` directory as
the CLI, so login state is shared.

**Prerequisites for building:** Python 3.11+ (for PyInstaller) and
Node.js 18+ (for Electron). Users who download the AppImage do NOT
need Python installed.

### Troubleshooting

**`ModuleNotFoundError: No module named 'rs3tk'`**

The venv setup failed or was skipped. From the repo root:

```bash
# Create a venv and install rs3tk
python3 -m venv ~/.config/rs3tk/venv
~/.config/rs3tk/venv/bin/pip install -e .
# Then restart the GUI
cd electron && npm run dev
```

**`electron-vite: not found` after `npm install`**

Your npm was configured to omit devDependencies (common in VMs with
`NODE_ENV=production`). The `electron/.npmrc` in this repo sets
`include=dev` to prevent this. Try:

```bash
rm -rf electron/node_modules && cd electron && npm install
```

**`The SUID sandbox helper binary was found, but is not configured correctly`**

This only happens on very old Electron builds or custom Linux
setups. The GUI disables the sandbox automatically. If you still
see it, run:

```bash
sudo chown root electron/node_modules/electron/dist/chrome-sandbox
sudo chmod 4755 electron/node_modules/electron/dist/chrome-sandbox
```

**Backend starts but GUI shows only loading spinners**

The backend took longer than expected to respond. The GUI retries
automatically (up to 15 attempts). If it persists, check that the
port 8765 is not already in use by another process:

```bash
lsof -i :8765
```

## License

MIT
