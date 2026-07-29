import { contextBridge, ipcRenderer } from 'electron'
import type { BridgeAPI } from './api'

/** Shape exposed to the renderer on `window.api`. */
interface RendererAPI extends BridgeAPI {
  minimize: () => void
  maximize: () => void
  close: () => void
  getVersion: () => Promise<string>
  setSettings: (settings: { closeToTray?: boolean; closeOnLaunch?: boolean }) => void
  setPersistentSettings: (settings: Record<string, unknown>) => void
  getPersistentSettings: () => Promise<Record<string, unknown>>
  notifyGameLaunched: () => void
  getSessionCookies: (url: string) => Promise<Array<Record<string, unknown>>>
}

const api: RendererAPI = {
  // ── bridge (JSON-RPC via the Python child process) ──
  getCharacters: () => ipcRenderer.invoke('api-call', 'get_characters'),
  getAccounts: () => ipcRenderer.invoke('api-call', 'get_accounts'),
  getClients: () => ipcRenderer.invoke('api-call', 'get_clients'),
  getStatus: () => ipcRenderer.invoke('api-call', 'get_status'),
  getMetrics: (name) => ipcRenderer.invoke('api-call', 'get_metrics', { name }),
  login: (systemBrowser = false) =>
    ipcRenderer.invoke('api-call', 'login', { system_browser: systemBrowser }),
  logout: (username, all = false) =>
    ipcRenderer.invoke('api-call', 'logout', { username, all }),
  launchGame: (clientKey: string, character: string) =>
    ipcRenderer.invoke('api-call', 'launch_game', { client_key: clientKey, character }),
  installClient: (clientKey: string) =>
    ipcRenderer.invoke('api-call', 'install_client', { client_key: clientKey }),

  // ── window controls ──
  minimize: () => ipcRenderer.send('minimize'),
  maximize: () => ipcRenderer.send('maximize'),
  close: () => ipcRenderer.send('close'),

  // ── app metadata ──
  getVersion: () => ipcRenderer.invoke('get-version'),
  notifyGameLaunched: () => ipcRenderer.send('launch-game'),

  // ── settings (window-local) ──
  setSettings: (settings) => ipcRenderer.send('set-settings', settings),
  setPersistentSettings: (settings) => ipcRenderer.send('set-persistent-settings', settings),
  getPersistentSettings: () => ipcRenderer.invoke('get-persistent-settings') as Promise<Record<string, unknown>>,

  // ── cookies (for OAuth flows) ──
  getSessionCookies: (url) => ipcRenderer.invoke('get-session-cookies', url),
}

if (process.contextIsolated) {
  contextBridge.exposeInMainWorld('api', api)
} else {
  ;(window as unknown as { api: RendererAPI }).api = api
}
