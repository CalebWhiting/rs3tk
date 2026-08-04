import { app, shell, BrowserWindow, ipcMain, session, Tray, Menu, nativeImage, screen, dialog } from 'electron'
import { join } from 'path'
import { ChildProcess, execSync as execSyncCb } from 'child_process'
import { readFile, writeFile, mkdir } from 'fs/promises'
import { existsSync } from 'fs'
import { homedir } from 'os'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import { Bridge } from './bridge'

if (process.platform === 'linux') {
  app.commandLine.appendSwitch('no-sandbox')
  app.commandLine.appendSwitch('disable-dev-shm-usage')
}

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
  lastCharacter?: string
  closeToTray?: boolean
  closeOnLaunch?: boolean
  disableEffects?: boolean
  trayLaunchMenu?: boolean
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

const ALLOWED_COOKIE_DOMAINS = ['runescape.com', 'jagex.com']

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
    return ALLOWED_COOKIE_DOMAINS.some((d) => host === d || host.endsWith('.' + d))
  } catch {
    return false
  }
}

const bridge = new Bridge()

let closeToTray = true
let closeOnLaunch = false
let trayLaunchMenuEnabled = false
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

function showError(title: string, message: string): void {
  console.error(`[${ts()}] [main] ${title}: ${message}`)
  dialog.showErrorBox(title, message)
}

function resolveBridgeCommand(): { command: string; args: string[] } {
  // Production: bundled binary inside the AppImage
  const bundled = join(process.resourcesPath, 'rs3tk-bridge')
  if (existsSync(bundled)) {
    return { command: bundled, args: [] }
  }

  // Dev: local venv at the monorepo root
  const monorepoRoot = join(__dirname, '..', '..', '..', '..')
  const devPy = join(monorepoRoot, '.venv', 'bin', 'python3')
  const devScript = join(monorepoRoot, 'packages', 'electron', 'src', 'bridge', 'rs3tk_bridge.py')
  if (existsSync(devPy) && existsSync(devScript)) {
    return { command: devPy, args: [devScript] }
  }

  throw new Error('rs3tk-bridge not found. Run `pnpm run setup-dev` or install the AppImage.')
}

function startBridge(): void {
  const { command, args } = resolveBridgeCommand()
  console.log(`[${ts()}] [main] Spawning bridge: ${command} ${args.join(' ')}`)
  bridge.start(command, args)
}

function stopBridge(): void {
  bridge.stop()
}

function getIconPath(): string {
  if (is.dev) {
    return join(__dirname, '..', '..', 'src', 'renderer', 'public', 'logo.png')
  }
  return join(__dirname, '..', 'renderer', 'logo.png')
}

function buildStaticMenu(): Menu {
  return Menu.buildFromTemplate([
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
        stopBridge()
        app.quit()
      }
    }
  ])
}

async function refreshTrayMenu(): Promise<void> {
  if (!tray) return

  if (!trayLaunchMenuEnabled || !bridge.isRunning()) {
    tray.setContextMenu(buildStaticMenu())
    return
  }

  try {
    const [clientsResult, charactersResult] = await Promise.all([
      bridge.call<Array<{ key: string; name: string; installed: boolean }>>('get_clients'),
      bridge.call<{ characters: Array<{ display_name: string; username: string; is_member: boolean }> }>('get_characters')
    ])

    const installedClients = clientsResult.filter((c) => c.installed)
    const characters = charactersResult.characters ?? []

    const template: Electron.MenuItemConstructorOptions[] = [
      {
        label: 'Show RS3TK',
        click: () => {
          if (mainWindow) {
            mainWindow.show()
            mainWindow.focus()
          }
        }
      },
      { type: 'separator' }
    ]

    if (installedClients.length === 0) {
      template.push({ label: 'Launch', enabled: false })
    } else if (characters.length === 0) {
      template.push({ label: 'Launch', enabled: false, toolTip: 'No characters logged in' })
    } else {
      template.push({
        label: 'Launch',
        submenu: installedClients.map((client) => ({
          label: client.name,
          submenu: characters.map((char) => ({
            label: char.display_name,
            click: () => {
              bridge
                .call('launch_game', { client_key: client.key, character: char.display_name })
                .then(() => {
                  if (closeOnLaunch && mainWindow) mainWindow.hide()
                })
                .catch((e) => console.error(`[${ts()}] [main] tray launch failed: ${e}`))
            }
          }))
        }))
      })
    }

    template.push({ type: 'separator' })
    template.push({
      label: 'Quit',
      click: () => {
        isQuitting = true
        closeToTray = false
        stopBridge()
        app.quit()
      }
    })

    tray.setContextMenu(Menu.buildFromTemplate(template))
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e)
    console.error(`[${ts()}] [main] refreshTrayMenu failed`, msg)
    tray.setContextMenu(buildStaticMenu())
  }
}

function createTray(): void {
  const iconPath = getIconPath()
  const icon = nativeImage.createFromPath(iconPath)
  tray = new Tray(icon)

  tray.setToolTip('RS3TK')
  tray.setContextMenu(buildStaticMenu())
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show()
      mainWindow.focus()
    }
  })

  refreshTrayMenu()
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

  // Forward renderer console output to the main process log in dev so
  // we can see JS errors in the terminal. Skipped in production to
  // avoid spamming the AppImage log.
  if (is.dev) {
    app.on('web-contents-created', (_event, contents) => {
      contents.on('console-message', (_e, level, message, line, source) => {
        const tag = ['DEBUG', 'INFO', 'WARN', 'ERROR'][level] ?? 'LOG'
        console.log(`[renderer:${tag}] ${message} (${source}:${line})`)
      })
      contents.on('render-process-gone', (_e, details) => {
        console.error(`[renderer] gone: ${JSON.stringify(details)}`)
      })
    })
  }

  await loadPersistentSettings()
  closeToTray = persistentSettings.closeToTray ?? true
  closeOnLaunch = persistentSettings.closeOnLaunch ?? false
  trayLaunchMenuEnabled = persistentSettings.trayLaunchMenu ?? false

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
    if (settings.trayLaunchMenu !== undefined) {
      trayLaunchMenuEnabled = settings.trayLaunchMenu
      refreshTrayMenu()
    }
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

  ipcMain.on('refresh-tray', () => {
    refreshTrayMenu()
  })

  ipcMain.handle('get-version', () => app.getVersion())

  ipcMain.handle('get-session-cookies', async (event, url: string) => {
    if (!isAllowedCookieDomain(url)) return []
    const cookies = await session.defaultSession.cookies.get({ url })
    return cookies
  })

  ipcMain.handle('api-call', async (_event, method: string, params?: Record<string, unknown>) => {
    try {
      console.log(`[${ts()}] [main] api-call: ${method}`)
      const result = await bridge.call(method, params ?? {})
      console.log(`[${ts()}] [main] api-call result: ${method} ok`)
      return result
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e)
      console.error(`[${ts()}] [main] api-call error: ${method}`, msg)
      return { error: msg }
    }
  })

  try {
    startBridge()
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    showError(
      'Bridge Setup Failed',
      `Could not start the rs3tk bridge:\n\n${message}\n\nThe application will close in 5 seconds.`
    )
    setTimeout(() => app.quit(), 5000)
    return
  }

  createWindow()
  createTray()
  console.log(`[${ts()}] [main] Bridge ready, window created, tray created`)

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('before-quit', () => {
  isQuitting = true
  stopBridge()
  destroyTray()
})

app.on('window-all-closed', () => {
  stopBridge()
  destroyTray()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

function handleShutdown(): void {
  isQuitting = true
  destroyTray()
  stopBridge()
  app.quit()
}

process.on('SIGTERM', handleShutdown)
process.on('SIGINT', handleShutdown)

} // end else gotTheLock
