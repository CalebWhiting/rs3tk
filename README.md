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
rs3tk auth login

# List your characters
rs3tk accounts list

# Launch a game
rs3tk play rs3               # RS3
rs3tk play official          # OSRS official
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
rs3tk news -n 10 --game rs3

# Show/update settings
rs3tk config set --game osrs --client runelite

# Show detected clients
rs3tk clients list

# Log out
rs3tk auth logout
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

| Client | Game | Platform |
|--------|------|----------|
| RS3 NXT | RS3 | Linux |
| OSRS Official | OSRS | Linux |
| RuneLite | OSRS | Linux |
| HDOS | OSRS | Linux |

## Configuration

Settings are stored at `~/.config/rs3tk/`.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linter
ruff check src/

# Format code
ruff format src/

# Type check
mypy src/
```

## License

MIT
