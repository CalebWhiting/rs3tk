import type { BridgeAPI } from '../../../preload/api'

declare module '*.css?inline' {
  const content: string
  export default content
}

declare global {
    interface Window {
      api: BridgeAPI & {
        minimize: () => void
        maximize: () => void
        close: () => void
        getVersion: () => Promise<string>
        setSettings: (settings: { closeToTray?: boolean; closeOnLaunch?: boolean }) => void
        setPersistentSettings: (settings: Record<string, unknown>) => void
        getPersistentSettings: () => Promise<Record<string, unknown>>
        notifyGameLaunched: () => void
        getSessionCookies: (url: string) => Promise<Array<Record<string, unknown>>>
        refreshTray: () => void
      }
    }
}

export {}
