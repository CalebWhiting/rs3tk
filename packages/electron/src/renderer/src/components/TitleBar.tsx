import { useTheme, useSlot, themes } from '../lib/theme'
import { SunIcon, GearIcon, CloseIcon } from './icons'

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
          <img src="logo.png" alt="RS3TK" className="w-9 h-9" />
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
            <SunIcon />
          </button>
          <div className="absolute top-full right-0 mt-2 px-2 py-1 bg-rs-bg-light border border-rs-border rounded text-xs text-rs-text whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 z-50">
            {theme.name}
          </div>
        </div>
        <button onClick={onSettings} aria-label="Settings" className="text-rs-muted hover:text-rs-gold text-sm w-9 h-9 flex items-center justify-center rounded transition-colors duration-150 cursor-pointer font-bold">
          <GearIcon />
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
          className="text-rs-muted hover:text-rs-text hover:bg-rs-red/80 w-9 h-9 flex items-center justify-center rounded transition-colors duration-150 cursor-pointer"
        >
          <CloseIcon />
        </button>
      </div>
    </div>
  )
}
