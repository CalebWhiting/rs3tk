---

## **Required Inputs**

1. **IMPLEMENTATION_PLAN**
   - Build an open-source Jagex Launcher replacement as a Python CLI tool (`rs3tk`) with multi-account OAuth2 authentication, game session management, and RS3/OSRS client launching (Official, RuneLite, HDOS). Add a fully functional Electron-based GUI launcher with theming, particle effects, custom wallpapers, and a settings system. The architecture uses a layered Python backend (`app.py` as single source of truth) exposed via an HTTP server (`backend.py` on `127.0.0.1:8765`), consumed by the Electron renderer through a three-hop proxy chain (renderer → preload IPC → main process → HTTP). The implementation proceeded in phases: core CLI + OAuth2 + multi-account → HTTP backend → Electron shell + React components → theme system with CSS variables → wallpaper-based themes with canvas particle animations → settings system → settings view UI.

2. **TECHNICAL_SPECIFICATION**
   - **Python 3.11+**, Linux-only, MIT license
   - **CLI**: Click framework, Rich for terminal output
   - **API models**: Pydantic v2 with `_BaseApiModel` alias generator (snake→camel) for Jagex API compatibility
   - **HTTP client**: httpx with asyncio for OAuth2 and RuneScape website API calls
   - **Secrets**: keyring OS integration, namespaced as `accounts/{username}/{key}`
   - **Electron**: electron-vite + React 18 + TypeScript 5.5 strict + Tailwind CSS 3.4
   - **Styling**: CSS custom properties on `document.documentElement`, consumed by Tailwind via `var(--rs-*)` references
   - **Theme system**: `Theme` interface with `id`, `name`, `vars` (CSS props), `css` (injected `<style>`), `slots` (component overrides: `background`, `titlebar`, `cardHeader`, `memberIcon`), `fontImports`
   - **Wallpaper themes**: Full-viewport background component with wallpaper image, radial vignette, canvas particle animation, semi-transparent content backdrop
   - **Backend**: Synchronous `http.server.HTTPServer` with allowlisted GET/POST endpoints, CORS headers, JSON serialization via `json.dumps(data, default=str)`
   - **Client detection**: Three-tier strategy — custom install dir (`~/.config/rs3tk/clients/{key}/`) → PATH via `shutil.which()` → explicit `_paths` fallback. `.exe` auto-runs with `wine`, `.jar` with `java -jar`
   - **Auth flow**: Two-step OAuth2 PKCE — authorization code exchange → consent ID token → session creation via POST to `auth.jagex.com/game-session/v1/sessions`
   - **Linting**: ruff (E, F, I, N, UP, B, SIM, ANN) + mypy strict for Python; TypeScript strict for Electron

3. **PROJECT_REQUEST**
   - Create an open-source replacement for the Jagex Launcher that supports multi-account management, OAuth2 authentication, and launching RS3/OSRS clients (Official, RuneLite, HDOS) on Linux. The tool should have both a CLI interface and a polished Electron GUI with theming support, particle effects, and custom wallpaper backgrounds. The GUI should display character data (skills, quests, activities, RuneMetrics), allow account switching, client selection, and game launching. Security must be maintained with keyring-based token storage, strict IPC isolation, and allowlisted API endpoints.

4. **PROJECT_RULES**
   - NEVER USE GIT COMMIT/PUSH WITHOUT EXPLICIT REQUEST
   - No comments unless asked
   - No emojis unless asked
   - Python: line length 120, ruff (E, F, I, N, UP, B, SIM, ANN) + mypy strict
   - Electron: TypeScript strict mode
   - keyring for secrets, never in config files
   - Pydantic for all API models
   - asyncio for httpx calls
   - Tailwind CSS for Electron styling
   - Run lint/typecheck after every edit: `source .venv/bin/activate && ruff check src/ && ruff format --check src/ && mypy src/` (Python) and `cd electron && npx tsc --noEmit` (Electron)

5. **EXISTING_CODE**
   - **Python CLI** (`src/rs3tk/`): `cli.py` (Click commands), `app.py` (shared business logic), `config.py` (XDG paths, Settings, AccountInfo, keyring), `jagex_api.py` (Pydantic models + OAuth2 API), `rs_api.py` (RuneScape website APIs), `clients.py` (config-driven game client launcher), `install.py` (ClientInstaller ABC + RS3/Official/RuneLite/HDOS installers), `game.py` (game status + news), `ui.py` (Rich interactive terminal UI), `backend.py` (HTTP backend for Electron), `auth/` (OAuth2 flow, browser login, system browser fallback, PKCE), `data/` (auto-update launchers for RS3/OSRS/RuneLite/HDOS)
   - **Electron GUI** (`electron/`): `src/main/index.ts` (Electron main process, backend lifecycle, IPC handlers, security), `src/renderer/src/` — `App.tsx` (root with ThemeProvider + settings), `components/` (TitleBar, CharacterHeader, AccountsPanel, ClientPanel, Dashboard, SkillsCard, QuestsCard, ActivityCard, MetricsCard, SettingsView, BottomBar, LoadingOverlay, NoiseBackground), `hooks/useData.ts` (data fetching), `lib/theme.tsx` (ThemeProvider, useTheme, useSlot, 7 themes), `lib/settings.ts` (localStorage), `lib/format.ts` (XP/number formatting), `themes/` (Raptor, Necromancy, City of Um wallpaper backgrounds with canvas particles), `styles/globals.css` (gold-button, member-symbol, text-shadow), `types/` (TypeScript interfaces)
   - **Themes**: RuneSlate (default), Oldschool, Darcula, Midnight, Raptor (wallpaper + golden embers), Necromancy (wallpaper + cyan orbs), City of Um (wallpaper + teal wisps)
   - **Settings**: Python CLI (`default_game`, `default_client`, `last_character`, `default_character`, `locale`, `accounts`); Electron GUI (`closeToTray`, `closeOnLaunch`, `disableEffects`)
   - **Backend API**: GET `/api/characters`, `/api/accounts`, `/api/clients`, `/api/metrics/{name}`, `/api/avatar/{name}`; POST `/api/launch`, `/api/login`, `/api/logout` (no username = logout all)

---
