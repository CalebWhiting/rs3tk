declare module '*.css?inline' {
  const content: string
  export default content
}

declare global {
  interface Window {
    api: {
      minimize: () => void
      maximize: () => void
      close: () => void
      getVersion: () => Promise<string>
      setSettings: (settings: { closeToTray?: boolean; closeOnLaunch?: boolean }) => void
      setPersistentSettings: (settings: Record<string, unknown>) => void
      getPersistentSettings: () => Promise<Record<string, unknown>>
      launchGame: () => void
      getSessionCookies: (url: string) => Promise<any[]>
      callBackend: (endpoint: string) => Promise<any>
      callBackendPost: (endpoint: string, body: unknown) => Promise<any>
    }
  }
}

export {}
