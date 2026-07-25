import { contextBridge, ipcRenderer } from 'electron'

const api = {
  minimize: () => ipcRenderer.send('minimize'),
  maximize: () => ipcRenderer.send('maximize'),
  close: () => ipcRenderer.send('close'),
  getVersion: () => ipcRenderer.invoke('get-version'),
  setSettings: (settings: { closeToTray?: boolean; closeOnLaunch?: boolean }) => ipcRenderer.send('set-settings', settings),
  setPersistentSettings: (settings: Record<string, unknown>) => ipcRenderer.send('set-persistent-settings', settings),
  getPersistentSettings: () => ipcRenderer.invoke('get-persistent-settings') as Promise<Record<string, unknown>>,
  launchGame: () => ipcRenderer.send('launch-game'),
  getSessionCookies: (url: string) => ipcRenderer.invoke('get-session-cookies', url),
  callBackend: (endpoint: string) => {
    return ipcRenderer.invoke('api-call', endpoint).then((result) => {
      return result
    })
  },
  callBackendPost: (endpoint: string, body: unknown) => {
    return ipcRenderer.invoke('api-post', endpoint, body).then((result) => {
      return result
    })
  }
}

if (process.contextIsolated) {
  contextBridge.exposeInMainWorld('api', api)
} else {
  ;(window as any).api = api
}
