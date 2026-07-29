# Architecture

The rs3tk monorepo has three modules and one bridge. This document
shows how they fit together.

## High-level

```
┌─────────────────────────────────────────────────────────────────────┐
│  rs3tk/          (one git repo, one release tag)                   │
│                                                                     │
│  packages/                                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ core/                          Python library                 │   │
│  │   rs3tk_core/                                              │   │
│  │     app.py, auth/, jagex_api.py, rs_api.py, ...            │   │
│  │   ────────────────────►  pip install rs3tk-core             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ▲                                      │
│                              │ depends on                           │
│  ┌──────────────────────┐    │    ┌─────────────────────────────┐    │
│  │ cli/                 │────┘    │ electron/                   │    │
│  │   rs3tk_cli/         │         │   src/                      │    │
│  │     cli.py (Click)   │         │     main/      ── TS        │    │
│  │     ui.py  (Rich)    │         │     preload/   ── TS        │    │
│  │   ──► pip install rs3tk         │     renderer/  ── React     │    │
│  └──────────────────────┘         │       rs3tk_bridge.py  ◄────│────┘
│                                   │       (stdio JSON-RPC)     │   │
│                                   │       electron_login/      │   │
│                                   │         main.js            │   │
│                                   │   ──► npm i rs3tk-electron │   │
│                                   │   ──► AppImage             │   │
│                                   └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

- **core** has no knowledge of HTTP, no public API, no Electron
  artefacts. It exports Python functions.
- **cli** depends on the core and provides all the Python
  user-facing entry points: `rs3tk` (Click) and `rs3tk ui` (Rich TUI).
- **electron** depends on the core via its local venv (dev) or
  PyInstaller bundle (prod). It owns its own bridge — a single Python
  file that calls `rs3tk_core.app` over a child-process stdio pipe.
  It also owns the headless login script that the core's optional
  `find_electron_login_script()` probe looks for on the user's system.

## The stdio JSON-RPC bridge

The bridge is the entirety of the electron app's contract with the
Python world. It is small, talks JSON-RPC 2.0 over stdio, and lives at
`packages/electron/src/bridge/rs3tk_bridge.py`.

### Wire protocol

```
Request:   {"id": <int>, "method": <str>, "params": <obj>}
Response:  {"id": <int>, "result": <any>}
Error:     {"id": <int|null>, "error": {"code": <int>, "message": <str>}}
Notify:    {"method": <str>, "params": <obj>}   (one-way, no response)
```

| Error code | Meaning                              |
|------------|--------------------------------------|
| -32700     | Parse error (malformed JSON)         |
| -32600     | Invalid request (missing method)     |
| -32601     | Method not found                     |
| -32000     | Server error (handler raised)        |

### Transport

```
Electron main process                Bridge child process
       │                                       │
       │  spawn(python, [rs3tk_bridge.py])     │
       │ ─────────────────────────────────────►│
       │                                       │
       │ {"id":1,"method":"get_characters",    │
       │  "params":{}}                         │
       │ ─────────────────────────────────────►│
       │                                       │ (calls rs3tk_core.app._get_characters_result)
       │ {"id":1,"result":{"characters":[...], │
       │  "auth_errors":[]}}                   │
       │ ◄─────────────────────────────────────│
```

Logs go to **stderr** with a `[bridge]` prefix; the Electron main
process pipes them into the Electron log.

### Adding a new method

1. Add a `@method("name")` decorated function to `rs3tk_bridge.py`.
2. Add the matching typed method to `BridgeAPI` in
   `packages/electron/src/preload/api.ts`.
3. Add a `window.api.<name> = ...` line in
   `packages/electron/src/preload/index.ts`.
4. Add a call to it in the renderer.
5. The bridge roundtrip test
   (`tests/test_bridge_roundtrip.py`) verifies the method is
   registered. If you forget step 2 or 3, the roundtrip test still
   passes (the bridge advertises the new method), but the renderer
   will get a TypeScript compile error.

### Where the bridge gets the Python

```typescript
function resolveBridgeCommand(): { command: string; args: string[] } {
  // Production: bundled binary inside the AppImage
  const bundled = join(process.resourcesPath, 'rs3tk-bridge')
  if (existsSync(bundled)) return { command: bundled, args: [] }

  // Dev: local venv at the monorepo root
  const devPy = join(monorepoRoot, '.venv', 'bin', 'python3')
  const devScript = join(monorepoRoot, 'packages', 'electron', 'src', 'bridge', 'rs3tk_bridge.py')
  if (existsSync(devPy) && existsSync(devScript)) {
    return { command: devPy, args: [devScript] }
  }

  throw new Error('rs3tk-bridge not found. Run `pnpm run setup-dev` or install the AppImage.')
}
```

Two paths, no five-step fallback ladder.

## Package map

| PyPI / npm name  | Import path      | Source                                |
|------------------|------------------|---------------------------------------|
| `rs3tk-core`     | `rs3tk_core.*`   | `packages/core/src/rs3tk_core/`       |
| `rs3tk`          | `rs3tk_cli.*`    | `packages/cli/src/rs3tk_cli/`         |
| `rs3tk-electron` | n/a              | `packages/electron/`                  |

The console script entry point is `rs3tk` (from
`rs3tk_cli.cli:main`).

## What this architecture kills

| Gone from the old repo                                | Why                                       |
|-------------------------------------------------------|-------------------------------------------|
| `BACKEND_PORT = 8765` constant                        | No port; stdio only                       |
| `fuser 8765/tcp` port-already-in-use check            | Nothing to bind                           |
| `waitForBackendReady()` socket-poll loop              | Child is ready the instant stdin is writable |
| `BACKEND_STARTUP_RETRIES` / exponential backoff       | The first call is never "not available"   |
| `ALLOWED_GET_ENDPOINTS` / `ALLOWED_POST_ENDPOINTS`    | `METHODS` in the bridge IS the allow-list |
| `OPTIONS` handler, CORS headers                       | Not a browser context                     |
| `ensureUserVenv` (pip-install fallback)               | AppImage always has the bundled binary    |
| `src/rs3tk/backend.py` and its `rs3tk-backend` script | The bridge replaces it                    |
| `src/rs3tk/auth/electron_login/` in the Python package | The login script moved to the electron module |

The renderer's `useData.ts` collapses from ~150 LOC with retry state
to ~30 LOC of plain `useEffect` + bridge call.
