export interface Settings {
  closeToTray: boolean
  closeOnLaunch: boolean
  disableEffects: boolean
  trayLaunchMenu: boolean
}

const STORAGE_KEY = 'rs3tk-settings'

const defaultSettings: Settings = {
  closeToTray: true,
  closeOnLaunch: false,
  disableEffects: false,
  trayLaunchMenu: false,
}

export function loadSettingsLocal(): Settings {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return { ...defaultSettings, ...JSON.parse(stored) }
    }
  } catch {}
  return { ...defaultSettings }
}

export function saveSettingsLocal(settings: Settings): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  } catch {}
}

let initialized = false
let initPromise: Promise<Settings> | null = null

export function initSettings(): Promise<Settings> {
  if (initPromise) return initPromise
  initPromise = (async () => {
    try {
      const remote = await window.api.getPersistentSettings()
      const merged = { ...defaultSettings, ...remote }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(merged))
      try { localStorage.setItem('rs3tk-disable-effects', String(merged.disableEffects)) } catch {}
      window.dispatchEvent(new CustomEvent('rs3tk-disable-effects', { detail: merged.disableEffects }))
      if (remote.closeToTray !== undefined) {
        window.api.setSettings({ closeToTray: merged.closeToTray, closeOnLaunch: merged.closeOnLaunch })
      }
      initialized = true
      return merged
    } catch {
      initialized = true
      return loadSettingsLocal()
    }
  })()
  return initPromise
}

export function loadSettings(): Settings {
  return loadSettingsLocal()
}

export function saveSettings(settings: Settings): void {
  saveSettingsLocal(settings)
  if (initialized) {
    try {
      window.api.setPersistentSettings({
        closeToTray: settings.closeToTray,
        closeOnLaunch: settings.closeOnLaunch,
        disableEffects: settings.disableEffects,
        trayLaunchMenu: settings.trayLaunchMenu,
      })
      window.api.setSettings({ closeToTray: settings.closeToTray, closeOnLaunch: settings.closeOnLaunch })
    } catch {}
  }
}

export function updateSetting<K extends keyof Settings>(key: K, value: Settings[K]): void {
  const settings = loadSettings()
  settings[key] = value
  saveSettings(settings)
  if (key === 'disableEffects') {
    try { localStorage.setItem('rs3tk-disable-effects', String(value)) } catch {}
    window.dispatchEvent(new CustomEvent('rs3tk-disable-effects', { detail: value }))
  }
}
