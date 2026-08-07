# Changelog

## v1.1.1

- **Fix Electron discovery for pip installs** — When Electron is installed
  globally via npm but the global bin directory is not on PATH (e.g.
  `~/.npm-global/bin`), the login flow now probes `npm root -g` to locate the
  binary. If the postinstall script didn't run, it triggers `install.js`
  automatically to download the missing binary.

- **Fix release artifact upload paths** — The release workflow now looks for
  AppImage/DEB/RPM artifacts in `.build/electron/` (where electron-builder
  actually outputs them) instead of `packages/electron/dist/`.

## v1.1.0

- **Launch presets** — Save named groups of client/character pairs and launch
  them all at once with `rs3tk play --preset <name>`. New CLI commands:
  `presets create`, `presets delete`, `presets show`, `presets list`,
  `presets add`. Presets are stored in `~/.config/rs3tk/presets.json`.

- **Character caching** — The play flow now caches character data to avoid
  redundant network fetches when switching between characters.

- **Electron cache location** — Moved the Electron user-data directory from
  `/tmp` to `~/.cache/rs3tk/electron-cache` for more reliable persistence.

- **Broader dependency compatibility** — Lowered the minimum `httpx` version
  to 0.25.1 and `keyring` to 22.0 for wider distro support.

- **Improved error messages** — The Java-not-found error for HDOS now shows
  the actual client name instead of a hardcoded string.

- **Electron packaging overhaul** — Simplified the build pipeline: removed
  the custom `after-pack.cjs` wrapper, switched to electron-builder's native
  RPM target, and split `build:linux` from `build:release` to handle Arch
  RPM incompatibility.

- **Build cleanup** — Consolidated build artifacts into `.build/`, removed
  tracked files that should be gitignored, and added a `clean.sh` script.

## v1.0.3

- **Login flow overhaul** — The OAuth login process was completely reworked. The
  system browser (manual URL paste) fallback was removed — login now always uses
  an embedded Electron window. This simplified the codebase significantly by
  merging the old "browser" and "system browser" modules into a single
  `electron_login` module.

- **Display name from JWT** — After logging in, your Jagex display name
  (e.g. "Alice#123") is now read directly from the consent token instead of
  making a separate API call. This is faster and more reliable.

- **Login script bundled with core** — The Electron login script
  (`electron_login.cjs`) now lives inside the core Python package instead of
  the Electron package. This means the CLI app no longer depends on the
  Electron package being present on disk.

- **Electron stability fixes** — A long series of fixes to make the Electron
  login window work reliably on Linux: disabled GPU acceleration (fixes VM
  hangs), disabled sandboxing (fixes AppArmor errors), fixed stderr pipe
  deadlocks, added a 5-minute timeout safety net, and improved argument
  parsing.

- **pnpm compatibility** — Fixed Electron and esbuild build scripts that broke
  under pnpm 9, and corrected the Electron binary lookup path for pnpm
  monorepos (it was looking in the wrong `node_modules` directory).

- **Dependency fix** — Added missing `libselinux1` to the RS3 client
  supplemental dependencies.

## v1.0.2

- **Linux packaging** — rs3tk now ships as native packages for Debian/Ubuntu
  (.deb), Arch Linux (PKGBUILD), Fedora/RHEL (RPM), and Alpine (APKBUILD), so
  you can install it with your system package manager instead of building from
  source.

- **Tray icon launch menu** — The system tray icon now has a Launch submenu
  letting you pick a client and character to start the game directly, without
  opening the full GUI.

- **Screenshots in README** — The README now includes screenshots of the
  Electron GUI so you can see what it looks like before installing.

- **CI/CD fixes** — A series of fixes to the release pipeline: corrected
  packaging metadata, fixed Linux package builds, fixed AppImage release
  uploads, and aligned tooling versions across CI jobs.

## v1.0.1

- **Remember last character** — The Electron launcher now remembers the last
  character you selected and pre-selects it next time.

- **Fix stdout pollution** — Fixed `launch_game` print statements leaking into
  the bridge's JSON-RPC protocol, which caused random disconnects.

- **Dev environment improvements** — Restructured test setup for clean
  fresh-environment testing, added dependency groups, and cleaned up docs.

## v1.0.0

Initial release.

### CLI

- OAuth2 login via Jagex accounts with PKCE + CSRF protection
- Account management: list, set-default, logout (single or all)
- Game client management: install, remove, set-default for Official, RuneLite,
  and HDOS clients
- `play` command with interactive character/client picker and auto-launch
- Game server status check with PSA display
- RS3 and OSRS news fetcher with configurable locale
- Configurable defaults for game, client, and locale
- Rich interactive terminal UI (`rs3tk ui`)

### Electron GUI

- Full graphical launcher with system tray integration
- Client/character management with one-click launch
- Account login with embedded Electron OAuth flow
- RuneMetrics skill and activity feeds
- Game news and server status display
- Auto-creates Python venv and installs dependencies on first run
- Bundled Python backend via PyInstaller (no manual `pip install` needed)
- Splash screen during backend setup
- Last-character memory

### Core

- Async Jagex API client with session management and token refresh
- JWT decode and validation for OAuth tokens
- Keyring-backed credential storage
- RuneLite, HDOS, Official, and RS3 client detection and launch
- RS3 sandboxed binary execution with bundled supplemental libraries
- Pydantic models for all API responses

### Infrastructure

- Monorepo with `uv` workspaces (Python) and pnpm (Node.js)
- CI: lint (ruff), typecheck (mypy), test (pytest), build (PyInstaller),
  release (.deb, .rpm, PKGBUILD, APKBUILD, AppImage)
- AUR and COPR package publishing
