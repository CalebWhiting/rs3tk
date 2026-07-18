# rs3tk

Open-source Jagex Launcher replacement written in Python.

A command-line tool to authenticate with your Jagex Account and launch
Old School RuneScape (Official, RuneLite, HDOS) or RuneScape 3.

## Features

- **Unified authentication** — Log in via your Jagex Account with OAuth2
- **Multiple clients** — Launch RS3, OSRS Official, RuneLite, or HDOS
- **Secure token storage** — Credentials stored in your OS keyring
- **Multi-account support** — Switch between characters
- **Browser login** — Opens your default browser for OAuth2 login
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
rs3tk login

# List your characters
rs3tk accounts

# Launch a game
rs3tk play rs3               # RS3
rs3tk play osrs              # OSRS official
rs3tk play runelite          # RuneLite
rs3tk play hdos              # HDOS

# Interactive mode (pick client and character)
rs3tk play -i

# Launch with a specific character
rs3tk play runelite -c "Cow31337Killer"

# Check game status
rs3tk status

# View latest news
rs3tk news
rs3tk news -n 10 -g rs3

# View/set settings
rs3tk config
rs3tk config set --game osrs --client runelite

# Show detected clients
rs3tk clients

# Log out
rs3tk logout
```

## Options

- `-v` / `--verbose` — Enable debug logging
- `-#` / `--censor` — Censor sensitive data (account IDs, etc.)
- `-c` / `--character` — Select a specific character

## Supported Clients

| Client | Game | Platform |
|--------|------|----------|
| RS3 NXT | RS3 | Windows, macOS, Linux |
| OSRS Official | OSRS | Windows, macOS, Linux |
| RuneLite | OSRS | Windows, macOS, Linux |
| HDOS | OSRS | Windows, macOS, Linux |

## Configuration

Settings are stored at:

- **Linux:** `~/.config/rs3tk/`
- **macOS:** `~/Library/Application Support/rs3tk/`
- **Windows:** `%LOCALAPPDATA%\rs3tk\`

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linter
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Type check
mypy src/

# Run tests
pytest
```

## License

MIT
