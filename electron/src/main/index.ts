import { app, shell, BrowserWindow, ipcMain, session, Tray, Menu, nativeImage, screen } from 'electron'
import { join } from 'path'
import { spawn, ChildProcess } from 'child_process'
import { readFile, writeFile, mkdir } from 'fs/promises'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'

app.commandLine.appendSwitch('disable-gpu')

interface PersistentSettings {
  theme?: string
  selectedClient?: string
  closeToTray?: boolean
  closeOnLaunch?: boolean
  disableEffects?: boolean
  windowBounds?: { x: number; y: number; width: number; height: number }
}

let persistentSettings: PersistentSettings = {}
let settingsPath = ''

async function loadPersistentSettings(): Promise<void> {
  try {
    const dir = app.getPath('userData')
    await mkdir(dir, { recursive: true })
    settingsPath = join(dir, 'rs3tk-settings.json')
    const data = await readFile(settingsPath, 'utf-8')
    persistentSettings = JSON.parse(data)
  } catch {
    persistentSettings = {}
  }
}

async function savePersistentSettings(): Promise<void> {
  try {
    if (!settingsPath) return
    await writeFile(settingsPath, JSON.stringify(persistentSettings, null, '\t'))
  } catch {}
}

const ALLOWED_GET_ENDPOINTS = new Set(['/api/characters', '/api/accounts', '/api/clients', '/api/status'])
const ALLOWED_GET_PREFIXES = ['/api/metrics/', '/api/avatar/']
const ALLOWED_POST_ENDPOINTS = new Set(['/api/launch', '/api/login', '/api/logout'])
const ALLOWED_COOKIE_DOMAINS = ['runescape.com', 'jagex.com']

function isAllowedEndpoint(endpoint: string, allowed: Set<string>, prefixes: string[] = []): boolean {
  return allowed.has(endpoint) || prefixes.some(p => endpoint.startsWith(p))
}

function isUrlSafe(url: string): boolean {
  try {
    const parsed = new URL(url)
    return parsed.protocol === 'https:'
  } catch {
    return false
  }
}

function isAllowedCookieDomain(url: string): boolean {
  try {
    const host = new URL(url).hostname
    return ALLOWED_COOKIE_DOMAINS.some(d => host === d || host.endsWith('.' + d))
  } catch {
    return false
  }
}

let backendProcess: ChildProcess | null = null
const BACKEND_PORT = 8765

let closeToTray = true
let closeOnLaunch = false
let mainWindow: BrowserWindow | null = null
let tray: Tray | null = null
let isQuitting = false
let boundsTimer: ReturnType<typeof setTimeout> | null = null

function ts(): string {
  return new Date().toISOString().replace('T', ' ').replace('Z', '')
}

function destroyTray(): void {
  if (tray) {
    tray.removeAllListeners()
    tray.destroy()
    tray = null
  }
}

function isBoundsOnScreen(bounds: { x: number; y: number; width: number; height: number }): boolean {
  const displays = screen.getAllDisplays()
  return displays.some((d) => {
    const { x, y, width, height } = d.bounds
    return (
      bounds.x < x + width &&
      bounds.y < y + height &&
      bounds.x + bounds.width > x &&
      bounds.y + bounds.height > y
    )
  })
}

function saveWindowBounds(): void {
  if (!mainWindow || mainWindow.isDestroyed() || mainWindow.isMaximized()) return
  if (boundsTimer) clearTimeout(boundsTimer)
  boundsTimer = setTimeout(() => {
    if (!mainWindow || mainWindow.isDestroyed()) return
    const bounds = mainWindow.getBounds()
    persistentSettings.windowBounds = bounds
    savePersistentSettings()
  }, 500)
}

function startBackend(): void {
  const projectRoot = join(__dirname, '..', '..', '..')
  const python = process.env.PYTHON_PATH || join(projectRoot, '.venv', 'bin', 'python3')
  console.log(`[${ts()}] [main] Starting backend: ${python}`)

  const { execSync } = require('child_process') as typeof import('child_process')
  try {
    const pids = execSync(`fuser ${BACKEND_PORT}/tcp 2>/dev/null`, { encoding: 'utf-8' }).trim()
    if (pids) {
      for (const pid of pids.split(/\s+/)) {
        try { process.kill(Number(pid), 'SIGTERM') } catch {}
      }
      console.log(`[${ts()}] [main] Killed old process(es) on port ${BACKEND_PORT}: ${pids}`)
    }
  } catch {}

  backendProcess = spawn(python, ['-m', 'rs3tk.backend', String(BACKEND_PORT)], {
    stdio: 'pipe',
    cwd: projectRoot,
    env: { ...process.env, PYTHONPATH: join(projectRoot, 'src') }
  })
  backendProcess.stdout?.on('data', (data) => console.log(`[${ts()}] [backend] ${data.toString().trim()}`))
  backendProcess.stderr?.on('data', (data) => console.error(`[${ts()}] [backend] ${data.toString().trim()}`))
  backendProcess.on('exit', (code) => {
    console.log(`[${ts()}] [backend] exited with code ${code}`)
    backendProcess = null
  })
}

function stopBackend(): void {
  if (backendProcess) {
    backendProcess.kill()
    backendProcess = null
  }
}

function createTray(): void {
  const iconPath = is.dev
    ? join(__dirname, '..', '..', 'src', 'renderer', 'public', 'logo.png')
    : join(__dirname, '..', 'renderer', 'logo.png')
  const icon = nativeImage.createFromPath(iconPath)
  tray = new Tray(icon)

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show RS3TK',
      click: () => {
        if (mainWindow) {
          mainWindow.show()
          mainWindow.focus()
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true
        closeToTray = false
        app.quit()
      }
    }
  ])

  tray.setToolTip('RS3TK')
  tray.setContextMenu(contextMenu)
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show()
      mainWindow.focus()
    }
  })
}

function createWindow(): BrowserWindow {
  const iconPath = is.dev
    ? join(__dirname, '..', '..', 'src', 'renderer', 'public', 'logo.png')
    : join(__dirname, '..', 'renderer', 'logo.png')

  const saved = persistentSettings.windowBounds
  const defaults = { width: 1200, height: 800 }
  let bounds: { width: number; height: number; x?: number; y?: number } = defaults

  if (saved && saved.width >= 895 && saved.height >= 600 && isBoundsOnScreen(saved)) {
    bounds = { width: saved.width, height: saved.height, x: saved.x, y: saved.y }
  }

  mainWindow = new BrowserWindow({
    ...bounds,
    minWidth: 895,
    minHeight: 600,
    show: false,
    frame: false,
    titleBarStyle: 'hidden',
    icon: iconPath,
    backgroundColor: '#0e171d',
    webPreferences: {
      preload: join(__dirname, '../preload/index.mjs'),
      sandbox: false,
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow!.show()
  })

  mainWindow.on('resize', saveWindowBounds)
  mainWindow.on('move', saveWindowBounds)

  mainWindow.on('close', (e) => {
    if (closeToTray && !isQuitting) {
      e.preventDefault()
      mainWindow!.hide()
    }
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    if (isUrlSafe(details.url)) {
      shell.openExternal(details.url)
    }
    return { action: 'deny' }
  })

  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }

  return mainWindow
}

app.whenReady().then(async () => {
  electronApp.setAppUserModelId('com.rs3tk')

  await loadPersistentSettings()
  closeToTray = persistentSettings.closeToTray ?? true
  closeOnLaunch = persistentSettings.closeOnLaunch ?? false

  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  ipcMain.on('minimize', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.minimize()
  })

  ipcMain.on('maximize', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    if (win?.isMaximized()) {
      win.unmaximize()
    } else {
      win?.maximize()
    }
  })

  ipcMain.on('close', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.close()
  })

  ipcMain.on('set-settings', (_event, settings: { closeToTray?: boolean; closeOnLaunch?: boolean }) => {
    if (settings.closeToTray !== undefined) closeToTray = settings.closeToTray
    if (settings.closeOnLaunch !== undefined) closeOnLaunch = settings.closeOnLaunch
  })

  ipcMain.on('set-persistent-settings', (_event, settings: Partial<PersistentSettings>) => {
    Object.assign(persistentSettings, settings)
    savePersistentSettings()
    if (settings.closeToTray !== undefined) closeToTray = settings.closeToTray
    if (settings.closeOnLaunch !== undefined) closeOnLaunch = settings.closeOnLaunch
  })

  ipcMain.handle('get-persistent-settings', () => {
    return { ...persistentSettings }
  })

  ipcMain.on('launch-game', (event) => {
    if (closeOnLaunch) {
      const win = BrowserWindow.fromWebContents(event.sender)
      win?.hide()
    }
  })

  ipcMain.handle('get-version', () => app.getVersion())

  ipcMain.handle('get-session-cookies', async (event, url: string) => {
    if (!isAllowedCookieDomain(url)) return []
    const cookies = await session.defaultSession.cookies.get({ url })
    return cookies
  })

  console.log(`[${ts()}] [main] Registering IPC handlers`)
  ipcMain.handle('api-call', async (event, endpoint: string) => {
    if (!isAllowedEndpoint(endpoint, ALLOWED_GET_ENDPOINTS, ALLOWED_GET_PREFIXES)) {
      return { error: 'Forbidden endpoint' }
    }
    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 5000)
      console.log(`[${ts()}] [main] api-call: ${endpoint}`)
      const response = await fetch(`http://127.0.0.1:${BACKEND_PORT}${endpoint}`, { signal: controller.signal })
      clearTimeout(timeout)
      const result = await response.json()
      console.log(`[${ts()}] [main] api-call result: ${endpoint} → ${JSON.stringify(result).slice(0, 120)}`)
      return result
    } catch (e) {
      console.log(`[${ts()}] [main] api-call error: ${endpoint} → ${e}`)
      return { error: 'Backend not available' }
    }
  })

  ipcMain.handle('api-post', async (event, endpoint: string, body: unknown) => {
    if (!isAllowedEndpoint(endpoint, ALLOWED_POST_ENDPOINTS)) {
      return { error: 'Forbidden endpoint' }
    }
    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 10000)
      console.log(`[${ts()}] [main] api-post: ${endpoint}`)
      const response = await fetch(`http://127.0.0.1:${BACKEND_PORT}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal
      })
      clearTimeout(timeout)
      const result = await response.json()
      console.log(`[${ts()}] [main] api-post result: ${endpoint} → ${JSON.stringify(result).slice(0, 120)}`)
      return result
    } catch (e) {
      console.log(`[${ts()}] [main] api-post error: ${endpoint} → ${e}`)
      return { error: 'Backend not available' }
    }
  })

  startBackend()
  createWindow()
  createTray()
  console.log(`[${ts()}] [main] Backend started, window created, tray created`)

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('before-quit', () => {
  isQuitting = true
  destroyTray()
})

app.on('window-all-closed', () => {
  stopBackend()
  destroyTray()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

function handleShutdown(): void {
  isQuitting = true
  destroyTray()
  stopBackend()
  app.quit()
}

process.on('SIGTERM', handleShutdown)
process.on('SIGINT', handleShutdown)
