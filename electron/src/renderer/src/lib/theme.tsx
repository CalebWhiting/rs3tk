import { createContext, useContext, useState, useEffect, type ReactNode, type ComponentType } from 'react'
import RaptorBackground from '../themes/raptor/RaptorBackground'
import NecromancyBackground from '../themes/necromancy/NecromancyBackground'
import CityOfUmBackground from '../themes/city-of-um/CityOfUmBackground'
import KharidEtBackground from '../themes/kharid-et/KharidEtBackground'
import AmberfellBackground from '../themes/amberfell/AmberfellBackground'
import SoulWarsBackground from '../themes/soul-wars/SoulWarsBackground'

export interface ThemeSlots {
  titlebar?: ComponentType<{ theme: Theme }>
  background?: ComponentType<{ theme: Theme; children: ReactNode }>
}

export interface Theme {
  id: string
  name: string
  vars: Record<string, string>
  css?: string
  slots?: ThemeSlots
  fontImports?: string[]
}

const defaultVars: Record<string, string> = {
  '--rs-font-display': "'Museo Sans', sans-serif",
  '--rs-radius': '8px',
  '--rs-radius-sm': '4px',
  '--rs-selected-glow': '0 0 0 1px var(--rs-gold)',
  '--rs-titlebar-gradient': 'linear-gradient(to bottom, transparent, rgba(0,0,0,0.15))',
  '--rs-member-symbol': '\\2605',
  '--rs-pie-complete': '#22C55E',
  '--rs-pie-started': '#3b82f6',
  '--rs-pie-not-started': '#eab308',
  '--rs-scroll-fade': 'var(--rs-bg)',
  '--rs-spinner': 'var(--rs-gold)',
}

export const themes: Theme[] = [
  {
    id: 'original',
    name: 'RuneSlate',
    vars: {
      '--rs-bg': '#0e171d',
      '--rs-bg-light': '#1a2332',
      '--rs-card': 'rgba(255, 255, 255, 0.03)',
      '--rs-card-hover': 'rgba(255, 255, 255, 0.06)',
      '--rs-divider': 'rgba(255, 255, 255, 0.06)',
      '--rs-text': '#ffffff',
      '--rs-muted': '#8E98A8',
      '--rs-header': '#8E98A8',
      '--rs-border': 'rgba(255, 255, 255, 0.1)',
      '--rs-gold': '#D6A445',
      '--rs-gold-light': '#E8C066',
      '--rs-gold-dark': '#B8892E',
      '--rs-green': '#22C55E',
      '--rs-blue': '#3b82f6',
      '--rs-yellow': '#eab308',
      '--rs-red': '#ef4444',
      '--rs-btn-text': '#0e171d',
      '--rs-gold-btn-start': '#ffe259',
      '--rs-gold-btn-mid': '#ffa751',
      '--rs-gold-btn-end': '#e08a1e',
      '--rs-gold-btn-border': '#7a4600',
      '--rs-gold-btn-text': '#1a0800',
      '--rs-gold-btn-text-shadow': 'rgba(255, 230, 150, 0.6)',
      '--rs-noise-r': '14',
      '--rs-noise-g': '23',
      '--rs-noise-b': '29',
    },
  },
  {
    id: 'oldschool',
    name: 'Oldschool',
    vars: {
      '--rs-bg': '#1e1b18',
      '--rs-bg-light': '#2e2820',
      '--rs-card': 'rgba(46, 40, 32, 0.85)',
      '--rs-card-hover': 'rgba(54, 47, 38, 0.95)',
      '--rs-divider': 'rgba(255, 255, 255, 0.06)',
      '--rs-text': '#ffffff',
      '--rs-muted': '#8E98A8',
      '--rs-header': '#8E98A8',
      '--rs-border': '#574930',
      '--rs-gold': '#ffcb05',
      '--rs-gold-light': '#ffcb05',
      '--rs-gold-dark': '#7e6302',
      '--rs-green': '#22C55E',
      '--rs-blue': '#3b82f6',
      '--rs-yellow': '#ffcb05',
      '--rs-red': '#ef4444',
      '--rs-btn-text': '#1e1b18',
      '--rs-gold-btn-start': '#ffe259',
      '--rs-gold-btn-mid': '#ffa751',
      '--rs-gold-btn-end': '#e08a1e',
      '--rs-gold-btn-border': '#7a4600',
      '--rs-gold-btn-text': '#1a0800',
      '--rs-gold-btn-text-shadow': 'rgba(255, 230, 150, 0.6)',
      '--rs-noise-r': '33',
      '--rs-noise-g': '29',
      '--rs-noise-b': '26',
    },
  },
  {
    id: 'darcula',
    name: 'Darcula',
    vars: {
      '--rs-bg': '#2B2B2B',
      '--rs-bg-light': '#3C3F41',
      '--rs-card': 'rgba(60, 63, 65, 0.6)',
      '--rs-card-hover': 'rgba(60, 63, 65, 0.9)',
      '--rs-divider': 'rgba(50, 50, 50, 0.8)',
      '--rs-text': '#A9B7C6',
      '--rs-muted': '#808080',
      '--rs-header': '#CC7832',
      '--rs-border': '#434343',
      '--rs-gold': '#CC7832',
      '--rs-gold-light': '#E8944A',
      '--rs-gold-dark': '#9A5A1E',
      '--rs-green': '#6A8759',
      '--rs-blue': '#6897BB',
      '--rs-yellow': '#E8944A',
      '--rs-red': '#CC7832',
      '--rs-btn-text': '#1A1A1A',
      '--rs-gold-btn-start': '#E8944A',
      '--rs-gold-btn-mid': '#CC7832',
      '--rs-gold-btn-end': '#9A5A1E',
      '--rs-gold-btn-border': '#6B3D0F',
      '--rs-gold-btn-text': '#1A1A1A',
      '--rs-gold-btn-text-shadow': 'rgba(232, 148, 74, 0.6)',
      '--rs-noise-r': '43',
      '--rs-noise-g': '43',
      '--rs-noise-b': '43',
    },
  },
  {
    id: 'midnight',
    name: 'Midnight',
    vars: {
      '--rs-bg': '#222831',
      '--rs-bg-light': '#393E46',
      '--rs-card': 'rgba(57, 62, 70, 0.6)',
      '--rs-card-hover': 'rgba(57, 62, 70, 0.9)',
      '--rs-divider': 'rgba(0, 173, 181, 0.2)',
      '--rs-text': '#EEEEEE',
      '--rs-muted': '#8E98A8',
      '--rs-header': '#00ADB5',
      '--rs-border': 'rgba(0, 173, 181, 0.25)',
      '--rs-gold': '#00ADB5',
      '--rs-gold-light': '#33C4D0',
      '--rs-gold-dark': '#008A8F',
      '--rs-green': '#00ADB5',
      '--rs-blue': '#00ADB5',
      '--rs-yellow': '#EEEEEE',
      '--rs-red': '#FF6B6B',
      '--rs-btn-text': '#222831',
      '--rs-gold-btn-start': '#33C4D0',
      '--rs-gold-btn-mid': '#00ADB5',
      '--rs-gold-btn-end': '#008A8F',
      '--rs-gold-btn-border': '#006670',
      '--rs-gold-btn-text': '#222831',
      '--rs-gold-btn-text-shadow': 'rgba(51, 196, 208, 0.6)',
      '--rs-noise-r': '34',
      '--rs-noise-g': '40',
      '--rs-noise-b': '49',
    },
  },
  {
    id: 'raptor',
    name: 'Raptor',
    vars: {
      '--rs-bg': '#0e1a2e',
      '--rs-bg-light': '#152535',
      '--rs-card': 'rgba(21, 37, 53, 0.85)',
      '--rs-card-hover': 'rgba(30, 50, 70, 0.95)',
      '--rs-divider': 'rgba(212, 165, 32, 0.12)',
      '--rs-text': '#e8e8f0',
      '--rs-muted': '#6a7a8a',
      '--rs-header': '#d4a520',
      '--rs-border': '#1e3550',
      '--rs-gold': '#d4a520',
      '--rs-gold-light': '#f0c040',
      '--rs-gold-dark': '#9a7a10',
      '--rs-green': '#5a9a4a',
      '--rs-blue': '#3a7bd5',
      '--rs-yellow': '#d4a520',
      '--rs-red': '#8a3030',
      '--rs-btn-text': '#0e1a2e',
      '--rs-gold-btn-start': '#f0c040',
      '--rs-gold-btn-mid': '#d4a520',
      '--rs-gold-btn-end': '#9a7a10',
      '--rs-gold-btn-border': '#6a5008',
      '--rs-gold-btn-text': '#0e1a2e',
      '--rs-gold-btn-text-shadow': 'rgba(240, 192, 64, 0.6)',
      '--rs-noise-r': '14',
      '--rs-noise-g': '26',
      '--rs-noise-b': '46',
    },
    css: `
      .raptor-vignette {
        background: radial-gradient(ellipse at center, transparent 30%, rgba(10, 15, 30, 0.7) 100%);
      }
      .raptor-content-backdrop {
        background: transparent;
        min-height: 100vh;
      }
      .raptor-status-bar {
        background: var(--rs-card);
        border: 1px solid var(--rs-border);
        border-radius: var(--rs-radius);
      }
      .gold-button {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.3), inset 0 -4px 6px rgba(106, 80, 8, 0.8), 0 4px 12px rgba(0, 0, 0, 0.5);
      }
      .gold-button:hover {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.4), inset 0 -4px 6px rgba(106, 80, 8, 0.8), 0 6px 16px rgba(0, 0, 0, 0.6), 0 0 20px rgba(212, 165, 32, 0.2);
      }
      .gold-button:active {
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.3), inset 0 -2px 4px rgba(106, 80, 8, 0.8), 0 2px 6px rgba(0, 0, 0, 0.5);
      }
      ::selection {
        background: rgba(212, 165, 32, 0.3);
        color: #e8e8f0;
      }
    `,
    slots: {
      background: RaptorBackground,
    },
  },
  {
    id: 'necromancy',
    name: 'Necromancy',
    vars: {
      '--rs-bg': '#0a1a20',
      '--rs-bg-light': '#152530',
      '--rs-card': 'rgba(21, 37, 48, 0.85)',
      '--rs-card-hover': 'rgba(30, 50, 60, 0.95)',
      '--rs-divider': 'rgba(0, 212, 212, 0.12)',
      '--rs-text': '#e0f0f0',
      '--rs-muted': '#5a7a8a',
      '--rs-header': '#00d4d4',
      '--rs-border': '#1a3a45',
      '--rs-gold': '#00d4d4',
      '--rs-gold-light': '#40ffff',
      '--rs-gold-dark': '#008a8a',
      '--rs-green': '#00d4d4',
      '--rs-blue': '#00b8d4',
      '--rs-yellow': '#00d4d4',
      '--rs-red': '#ffa040',
      '--rs-btn-text': '#0a1a20',
      '--rs-gold-btn-start': '#40ffff',
      '--rs-gold-btn-mid': '#00d4d4',
      '--rs-gold-btn-end': '#008a8a',
      '--rs-gold-btn-border': '#005a5a',
      '--rs-gold-btn-text': '#0a1a20',
      '--rs-gold-btn-text-shadow': 'rgba(64, 255, 255, 0.6)',
      '--rs-noise-r': '10',
      '--rs-noise-g': '26',
      '--rs-noise-b': '32',
    },
    css: `
      .gold-button {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.3), inset 0 -4px 6px rgba(0, 60, 60, 0.8), 0 4px 12px rgba(0, 0, 0, 0.5);
      }
      .gold-button:hover {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.4), inset 0 -4px 6px rgba(0, 60, 60, 0.8), 0 6px 16px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 212, 212, 0.2);
      }
      .gold-button:active {
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.3), inset 0 -2px 4px rgba(0, 60, 60, 0.8), 0 2px 6px rgba(0, 0, 0, 0.5);
      }
      .necromancy-status-bar {
        background: rgba(10, 26, 32, 0.9);
        border: 1px solid var(--rs-border);
        border-radius: var(--rs-radius);
      }
      ::selection {
        background: rgba(0, 212, 212, 0.3);
        color: #e0f0f0;
      }
    `,
    slots: {
      background: NecromancyBackground,
    },
  },
  {
    id: 'city-of-um',
    name: 'City of Um',
    vars: {
      '--rs-bg': '#050d18',
      '--rs-bg-light': '#0a1828',
      '--rs-card': 'rgba(10, 24, 40, 0.85)',
      '--rs-card-hover': 'rgba(15, 35, 55, 0.95)',
      '--rs-divider': 'rgba(0, 180, 160, 0.1)',
      '--rs-text': '#d8e8e8',
      '--rs-muted': '#5a7a78',
      '--rs-header': '#00b4a0',
      '--rs-border': '#0e2a30',
      '--rs-gold': '#00b4a0',
      '--rs-gold-light': '#40e8d0',
      '--rs-gold-dark': '#007868',
      '--rs-green': '#40ffa0',
      '--rs-blue': '#00b4a0',
      '--rs-yellow': '#40e8d0',
      '--rs-red': '#ff6060',
      '--rs-btn-text': '#050d18',
      '--rs-gold-btn-start': '#40e8d0',
      '--rs-gold-btn-mid': '#00b4a0',
      '--rs-gold-btn-end': '#007868',
      '--rs-gold-btn-border': '#004840',
      '--rs-gold-btn-text': '#050d18',
      '--rs-gold-btn-text-shadow': 'rgba(64, 232, 208, 0.6)',
      '--rs-noise-r': '5',
      '--rs-noise-g': '13',
      '--rs-noise-b': '24',
    },
    css: `
      .gold-button {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.3), inset 0 -4px 6px rgba(0, 50, 50, 0.8), 0 4px 12px rgba(0, 0, 0, 0.5);
      }
      .gold-button:hover {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.4), inset 0 -4px 6px rgba(0, 50, 50, 0.8), 0 6px 16px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 180, 160, 0.2);
      }
      .gold-button:active {
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.3), inset 0 -2px 4px rgba(0, 50, 50, 0.8), 0 2px 6px rgba(0, 0, 0, 0.5);
      }
      ::selection {
        background: rgba(0, 180, 160, 0.3);
        color: #d8e8e8;
      }
    `,
    slots: {
      background: CityOfUmBackground,
    },
  },
  {
    id: 'kharid-et',
    name: 'Kharid-et',
    vars: {
      '--rs-bg': '#1e1028',
      '--rs-bg-light': '#2a1838',
      '--rs-card': 'rgba(42, 24, 56, 0.85)',
      '--rs-card-hover': 'rgba(55, 32, 72, 0.95)',
      '--rs-divider': 'rgba(192, 112, 224, 0.12)',
      '--rs-text': '#e8d8f0',
      '--rs-muted': '#9a80a8',
      '--rs-header': '#c070e0',
      '--rs-border': '#3a2848',
      '--rs-gold': '#d4a050',
      '--rs-gold-light': '#e8b860',
      '--rs-gold-dark': '#b08030',
      '--rs-green': '#80c070',
      '--rs-blue': '#7090d0',
      '--rs-yellow': '#d4a050',
      '--rs-red': '#d06080',
      '--rs-btn-text': '#1e1028',
      '--rs-gold-btn-start': '#e8b860',
      '--rs-gold-btn-mid': '#d4a050',
      '--rs-gold-btn-end': '#b08030',
      '--rs-gold-btn-border': '#806020',
      '--rs-gold-btn-text': '#1e1028',
      '--rs-gold-btn-text-shadow': 'rgba(232, 184, 96, 0.6)',
      '--rs-noise-r': '30',
      '--rs-noise-g': '16',
      '--rs-noise-b': '40',
    },
    css: `
      .gold-button {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.25), inset 0 -4px 6px rgba(80, 40, 100, 0.7), 0 4px 12px rgba(0, 0, 0, 0.5);
      }
      .gold-button:hover {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.35), inset 0 -4px 6px rgba(80, 40, 100, 0.7), 0 6px 16px rgba(0, 0, 0, 0.6), 0 0 20px rgba(192, 112, 224, 0.15);
      }
      .gold-button:active {
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.25), inset 0 -2px 4px rgba(80, 40, 100, 0.7), 0 2px 6px rgba(0, 0, 0, 0.5);
      }
      ::selection {
        background: rgba(192, 112, 224, 0.3);
        color: #e8d8f0;
      }
    `,
    slots: {
      background: KharidEtBackground,
    },
  },
  {
    id: 'amberfell',
    name: 'Amberfell',
    vars: {
      '--rs-bg': '#2a2010',
      '--rs-bg-light': '#3a3018',
      '--rs-card': 'rgba(50, 40, 20, 0.85)',
      '--rs-card-hover': 'rgba(60, 50, 28, 0.95)',
      '--rs-divider': 'rgba(96, 200, 224, 0.12)',
      '--rs-text': '#e8e0d0',
      '--rs-muted': '#9a8a6a',
      '--rs-header': '#60c8e0',
      '--rs-border': '#4a3a20',
      '--rs-gold': '#c8a050',
      '--rs-gold-light': '#e0b860',
      '--rs-gold-dark': '#a08030',
      '--rs-green': '#70b860',
      '--rs-blue': '#40a8d0',
      '--rs-yellow': '#c8a050',
      '--rs-red': '#c86050',
      '--rs-btn-text': '#1a1408',
      '--rs-gold-btn-start': '#e0b860',
      '--rs-gold-btn-mid': '#c8a050',
      '--rs-gold-btn-end': '#a08030',
      '--rs-gold-btn-border': '#706020',
      '--rs-gold-btn-text': '#1a1408',
      '--rs-gold-btn-text-shadow': 'rgba(224, 184, 96, 0.6)',
      '--rs-noise-r': '42',
      '--rs-noise-g': '32',
      '--rs-noise-b': '16',
    },
    css: `
      .gold-button {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.3), inset 0 -4px 6px rgba(80, 60, 20, 0.7), 0 4px 12px rgba(0, 0, 0, 0.5);
      }
      .gold-button:hover {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.4), inset 0 -4px 6px rgba(80, 60, 20, 0.7), 0 6px 16px rgba(0, 0, 0, 0.6), 0 0 20px rgba(96, 200, 224, 0.15);
      }
      .gold-button:active {
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.3), inset 0 -2px 4px rgba(80, 60, 20, 0.7), 0 2px 6px rgba(0, 0, 0, 0.5);
      }
      ::selection {
        background: rgba(96, 200, 224, 0.3);
        color: #e8e0d0;
      }
    `,
    slots: {
      background: AmberfellBackground,
    },
  },
  {
    id: 'soul-wars',
    name: 'Soul Wars',
    vars: {
      '--rs-bg': '#0a0e1a',
      '--rs-bg-light': '#121a2a',
      '--rs-card': 'rgba(18, 26, 42, 0.85)',
      '--rs-card-hover': 'rgba(25, 35, 55, 0.95)',
      '--rs-divider': 'rgba(0, 180, 200, 0.1)',
      '--rs-text': '#dce8f0',
      '--rs-muted': '#6a7a90',
      '--rs-header': '#00d4e0',
      '--rs-border': '#1a2a3a',
      '--rs-gold': '#d050a0',
      '--rs-gold-light': '#e870c0',
      '--rs-gold-dark': '#a03080',
      '--rs-green': '#40c8a0',
      '--rs-blue': '#00c8e0',
      '--rs-yellow': '#e0a0e8',
      '--rs-red': '#e05070',
      '--rs-btn-text': '#0a0e1a',
      '--rs-gold-btn-start': '#e870c0',
      '--rs-gold-btn-mid': '#d050a0',
      '--rs-gold-btn-end': '#a03080',
      '--rs-gold-btn-border': '#702060',
      '--rs-gold-btn-text': '#0a0e1a',
      '--rs-gold-btn-text-shadow': 'rgba(232, 112, 192, 0.6)',
      '--rs-noise-r': '10',
      '--rs-noise-g': '14',
      '--rs-noise-b': '26',
    },
    css: `
      .gold-button {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.3), inset 0 -4px 6px rgba(80, 20, 60, 0.8), 0 4px 12px rgba(0, 0, 0, 0.5);
      }
      .gold-button:hover {
        box-shadow: inset 0 2px 1px rgba(255, 255, 255, 0.4), inset 0 -4px 6px rgba(80, 20, 60, 0.8), 0 6px 16px rgba(0, 0, 0, 0.6), 0 0 20px rgba(208, 80, 160, 0.2);
      }
      .gold-button:active {
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.3), inset 0 -2px 4px rgba(80, 20, 60, 0.8), 0 2px 6px rgba(0, 0, 0, 0.5);
      }
      ::selection {
        background: rgba(208, 80, 160, 0.3);
        color: #dce8f0;
      }
    `,
    slots: {
      background: SoulWarsBackground,
    },
  },
]

const ThemeContext = createContext<{
  theme: Theme
  setTheme: (id: string) => void
}>({
  theme: themes[0],
  setTheme: () => {},
})

const styleTagId = 'rs3tk-theme-css'
const fontTagId = 'rs3tk-theme-fonts'

function removeElementById(id: string) {
  const el = document.getElementById(id)
  if (el) el.remove()
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [themeId, setThemeId] = useState(() => {
    try { return localStorage.getItem('rs3tk-theme') || 'original' } catch { return 'original' }
  })

  const theme = themes.find(t => t.id === themeId) || themes[0]

  useEffect(() => {
    window.api.getPersistentSettings().then((settings) => {
      if (settings.theme && typeof settings.theme === 'string' && settings.theme !== themeId) {
        setThemeId(settings.theme)
      }
    }).catch(() => {})
  }, [])

  useEffect(() => {
    try {
      localStorage.setItem('rs3tk-theme', themeId)
      window.api.setPersistentSettings({ theme: themeId })
    } catch {}
    const root = document.documentElement
    const vars = [
      ...Object.entries(defaultVars),
      ...Object.entries(theme.vars),
    ].map(([k, v]) => `${k}: ${v}`).join('; ')
    root.style.cssText = vars

    removeElementById(styleTagId)
    if (theme.css) {
      const style = document.createElement('style')
      style.id = styleTagId
      style.textContent = theme.css
      document.head.appendChild(style)
    }

    removeElementById(fontTagId)
    if (theme.fontImports?.length) {
      theme.fontImports.forEach((href, i) => {
        const link = document.createElement('link')
        link.id = `${fontTagId}-${i}`
        link.rel = 'stylesheet'
        link.href = href
        document.head.appendChild(link)
      })
    }

    return () => {
      removeElementById(styleTagId)
      theme.fontImports?.forEach((_, i) => removeElementById(`${fontTagId}-${i}`))
    }
  }, [themeId, theme])

  return (
    <ThemeContext.Provider value={{ theme, setTheme: setThemeId }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  return useContext(ThemeContext)
}

export function useSlot<K extends keyof ThemeSlots>(slotName: K): ThemeSlots[K] | undefined {
  const { theme } = useContext(ThemeContext)
  return theme.slots?.[slotName]
}
