import { useTheme, useSlot, themes } from '../lib/theme'

interface Props {
  onSettings: () => void
}

export default function TitleBar({ onSettings }: Props) {
  const { theme, setTheme } = useTheme()
  const TitlebarSlot = useSlot('titlebar')

  const cycleTheme = () => {
    const currentIndex = themes.findIndex(t => t.id === theme.id)
    const nextIndex = (currentIndex + 1) % themes.length
    setTheme(themes[nextIndex].id)
  }

  if (TitlebarSlot) {
    return <TitlebarSlot theme={theme} />
  }

  return (
    <div className="h-[60px] flex items-center justify-between px-6 border-b border-rs-border drag-region"
         style={{ background: 'var(--rs-titlebar-gradient)' }}>
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 flex items-center justify-center">
          <img src="/logo.png" alt="RS3TK" className="w-9 h-9" />
        </div>
        <span className="text-lg font-bold">RS3TK</span>
      </div>
      <div className="flex items-center gap-1 no-drag">
        <div className="relative group">
          <button
            onClick={cycleTheme}
            aria-label="Cycle theme"
            className="text-rs-muted hover:text-rs-gold text-sm w-9 h-9 flex items-center justify-center rounded transition-colors duration-150 cursor-pointer font-bold"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
          </button>
          <div className="absolute top-full right-0 mt-2 px-2 py-1 bg-rs-bg-light border border-rs-border rounded text-xs text-rs-text whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 z-50">
            {theme.name}
          </div>
        </div>
        <button onClick={onSettings} aria-label="Settings" className="text-rs-muted hover:text-rs-gold text-sm w-9 h-9 flex items-center justify-center rounded transition-colors duration-150 cursor-pointer font-bold">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
        </button>
        <button
          onClick={() => window.api.minimize()}
          aria-label="Minimize"
          className="text-rs-muted hover:text-rs-text text-lg w-9 h-9 flex items-center justify-center rounded transition-colors duration-150 cursor-pointer"
        >
          −
        </button>
        <button
          onClick={() => window.api.maximize()}
          aria-label="Maximize"
          className="text-rs-muted hover:text-rs-text text-lg w-9 h-9 flex items-center justify-center rounded transition-colors duration-150 cursor-pointer"
        >
          □
        </button>
        <button
          onClick={() => window.api.close()}
          aria-label="Close"
          className="text-rs-muted hover:text-rs-text hover:bg-rs-red/80 text-lg w-9 h-9 flex items-center justify-center rounded transition-colors duration-150 cursor-pointer"
        >
          ×
        </button>
      </div>
    </div>
  )
}
