const { app, BrowserWindow } = require('electron');
const path = require('path');

// Electron may or may not consume flags like --no-sandbox from argv,
// shifting indices.  Strip flag args and take the three positional args.
const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
const AUTH_URL = args[0];
const REDIRECT_HOST = args[1];
const USER_DATA_DIR = args[2] ? path.resolve(args[2]) : undefined;

if (!AUTH_URL || !REDIRECT_HOST || !USER_DATA_DIR) {
    console.error(JSON.stringify({ error: 'Missing arguments', argv: process.argv }));
    app.quit();
    process.exit(1);
}

app.setPath('userData', USER_DATA_DIR);

let mainWindow = null;

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

    mainWindow.webContents.on('did-finish-load', () => {
        checkUrl();
    });

    mainWindow.webContents.on('will-redirect', (event, redirectUrl) => {
        handleUrl(redirectUrl);
    });

    mainWindow.webContents.on('will-navigate', (event, navUrl) => {
        handleUrl(navUrl);
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
        app.quit();
    });
}

function checkUrl() {
    if (!mainWindow) return;

    mainWindow.webContents.executeJavaScript('window.location.href')
        .then((currentUrl) => {
            handleUrl(currentUrl);
        })
        .catch(() => {});
}

function handleUrl(navigationUrl) {
    try {
        const parsed = new URL(navigationUrl);

        // Step 1: launcher-redirect with auth code
        if (REDIRECT_HOST === 'secure.runescape.com' &&
            parsed.href.includes('launcher-redirect') &&
            parsed.searchParams.has('code')) {
            const result = {
                code: parsed.searchParams.get('code'),
                state: parsed.searchParams.get('state'),
            };
            console.log(JSON.stringify(result));
            app.quit();
            return;
        }

        // Step 2: localhost with id_token in fragment
        if (REDIRECT_HOST === 'localhost' && parsed.hostname === 'localhost') {
            const fragment = parsed.hash.substring(1); // Remove #
            if (fragment && fragment.includes('id_token=')) {
                const params = new URLSearchParams(fragment);
                const result = {
                    id_token: params.get('id_token'),
                    state: params.get('state'),
                };
                console.log(JSON.stringify(result));
                app.quit();
                return;
            }
        }
    } catch (e) {
        // Ignore URL parse errors
    }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    app.quit();
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});
