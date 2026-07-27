import { app, shell, BrowserWindow, ipcMain, session, Tray, Menu, nativeImage, screen, dialog } from 'electron'
import { join } from 'path'
import { spawn, execSync, ChildProcess } from 'child_process'
import { readFile, writeFile, mkdir } from 'fs/promises'
import { existsSync } from 'fs'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'

const gotTheLock = app.requestSingleInstanceLock()

if (!gotTheLock) {
  app.quit()
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.show()
      mainWindow.focus()
    }
  })

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
const ALLOWED_POST_ENDPOINTS = new Set(['/api/launch', '/api/login', '/api/logout', '/api/install'])
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
  console.log(`[${ts()}] [main] Starting backend`)

  const { execSync } = require('child_process') as typeof import('child_process')

  try {
    execSync(`fuser ${BACKEND_PORT}/tcp 2>/dev/null`, { encoding: 'utf-8' })
    console.log(`[${ts()}] [main] Backend already running on port ${BACKEND_PORT}`)
    return
  } catch {}

  const venvLocations = is.dev
    ? [join(__dirname, '..', '..', '..', '.venv', 'bin', 'python3')]
    : [
        join(app.getPath('exe'), '..', '..', '..', '..', '.venv', 'bin', 'python3'),
        join(app.getPath('exe'), '..', '..', '..', '.venv', 'bin', 'python3'),
        join(app.getPath('exe'), '..', '..', '.venv', 'bin', 'python3'),
      ]

  for (const venvPython of venvLocations) {
    if (existsSync(venvPython)) {
      const projectRoot = join(venvPython, '..', '..', '..')
      spawnBackend(venvPython, ['-m', 'rs3tk.backend', String(BACKEND_PORT)], projectRoot, { ...process.env, PYTHONPATH: join(projectRoot, 'src') })
      return
    }
  }

  try {
    const backendBin = execSync('which rs3tk-backend 2>/dev/null', { encoding: 'utf-8' }).trim()
    if (backendBin) {
      spawnBackend(backendBin, [String(BACKEND_PORT)], process.cwd(), process.env as Record<string, string>)
      return
    }
  } catch {}

  try {
    const py = execSync('which python3 2>/dev/null', { encoding: 'utf-8' }).trim()
    if (py) {
      spawnBackend(py, ['-m', 'rs3tk.backend', String(BACKEND_PORT)], process.cwd(), process.env as Record<string, string>)
      return
    }
  } catch {}

  console.error(`[${ts()}] [main] Could not find Python or rs3tk-backend`)
  dialog.showErrorBox(
    'Backend Not Found',
    'Could not find rs3tk-backend or Python with rs3tk installed.\n\n'
    + 'Install rs3tk with: pip install rs3tk\n\n'
    + 'The application will open but cannot function without the backend.'
  )
}

function spawnBackend(command: string, args: string[], cwd: string, env: Record<string, string>): void {
  console.log(`[${ts()}] [main] Spawning: ${command} ${args.join(' ')}`)
  backendProcess = spawn(command, args, {
    stdio: 'pipe',
    cwd,
    env
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
    backendProcess.stdout?.removeAllListeners()
    backendProcess.stderr?.removeAllListeners()
    backendProcess.removeAllListeners()
    backendProcess.kill()
    backendProcess = null
  }
}

function getIconPath(): string {
  if (is.dev) {
    return join(__dirname, '..', '..', 'src', 'renderer', 'public', 'logo.png')
  }
  return join(__dirname, '..', 'renderer', 'logo.png')
}

function createTray(): void {
  const iconPath = getIconPath()
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
        stopBackend()
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
  const iconPath = getIconPath()

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
      console.log(`[${ts()}] [main] api-call result: ${endpoint} ok`)
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
      console.log(`[${ts()}] [main] api-post result: ${endpoint} ok`)
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
  stopBackend()
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

} // end else gotTheLock
