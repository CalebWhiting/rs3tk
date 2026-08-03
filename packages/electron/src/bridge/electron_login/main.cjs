/**
 * Headless Electron window for Jagex OAuth2 login/consent.
 *
 * Spawned by the Python electron_login.py module. Receives three positional
 * arguments after the script path:
 *   1. URL — the OAuth2 authorization or consent URL
 *   2. redirectHost — expected hostname in the redirect (secure.runescape.com or localhost)
 *   3. userDataDir — path for Electron's user data (cookies, cache, etc.)
 *
 * Outputs a single JSON line to stdout with the result:
 *   Login:  { "code": "...", "state": "..." }
 *   Consent: { "id_token": "...", "state": "..." }
 *
 * Exits with code 0 on success, 1 on error.
 */

const { app, BrowserWindow } = require('electron');
const path = require('path');

// --- Argument parsing ---
// Electron inserts flags (--no-sandbox, --no-zygote, etc.) into process.argv
// before our positional args. Find the script path by looking for .cjs/.js,
// then read the three app arguments that follow it.
const scriptIdx = process.argv.findIndex((a) => a.endsWith('.cjs') || a.endsWith('.js'));
const args = process.argv.slice(scriptIdx + 1);

const AUTH_URL = args[0];
const REDIRECT_HOST = args[1];
const USER_DATA_DIR = args[2] ? path.resolve(args[2]) : undefined;

if (!AUTH_URL || !REDIRECT_HOST || !USER_DATA_DIR) {
    console.error(JSON.stringify({ error: 'Missing arguments', argv: process.argv }));
    app.quit();
    process.exit(1);
}

// --- Electron config ---
app.commandLine.appendSwitch('disable-gpu');
app.setPath('userData', USER_DATA_DIR);

let mainWindow = null;

function log(msg) {
    process.stderr.write(`[electron-login] ${msg}\n`);
}

function emitResult(result) {
    console.log(JSON.stringify(result));
    app.quit();
}

function handleUrl(urlString) {
    try {
        const parsed = new URL(urlString);

        // Phase 1: launcher-redirect with auth code
        if (REDIRECT_HOST === 'secure.runescape.com' &&
            parsed.href.includes('launcher-redirect') &&
            parsed.searchParams.has('code')) {
            emitResult({
                code: parsed.searchParams.get('code'),
                state: parsed.searchParams.get('state'),
            });
            return;
        }

        // Phase 2: localhost with id_token in fragment
        if (REDIRECT_HOST === 'localhost' && parsed.hostname === 'localhost') {
            const fragment = parsed.hash.substring(1);
            if (fragment && fragment.includes('id_token=')) {
                const params = new URLSearchParams(fragment);
                emitResult({
                    id_token: params.get('id_token'),
                    state: params.get('state'),
                });
                return;
            }
        }
    } catch {
        // Ignore URL parse errors (about:blank, chrome://, etc.)
    }
}

function checkCurrentUrl() {
    if (!mainWindow) return;
    mainWindow.webContents
        .executeJavaScript('window.location.href')
        .then((url) => handleUrl(url))
        .catch(() => {});
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        },
    });

    mainWindow.loadURL(AUTH_URL);

    mainWindow.webContents.on('did-finish-load', checkCurrentUrl);
    mainWindow.webContents.on('will-redirect', (_event, redirectUrl) => handleUrl(redirectUrl));
    mainWindow.webContents.on('will-navigate', (_event, navUrl) => handleUrl(navUrl));

    mainWindow.on('closed', () => {
        mainWindow = null;
        app.quit();
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => app.quit());

app.on('activate', () => {
    if (mainWindow === null) createWindow();
});

// Timeout safety net: if nothing resolves within 5 minutes, exit cleanly.
setTimeout(() => {
    log('Timeout reached (300s) — exiting.');
    app.quit();
}, 300_000);
