import { useState } from 'react'
import { useTheme, themes } from '../lib/theme'
import { loadSettings, updateSetting, type Settings } from '../lib/settings'
import { logout } from '../hooks/useData'
import type { Account } from '../types'
import { CloseIcon } from './icons'
import { SECTION_TITLE } from '../lib/styles'

interface Props {
  accounts: Account[]
  onClose: () => void
  onSettingsChanged: () => void
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: () => void }) {
  return (
    <button
      onClick={onChange}
      className={`w-10 h-5 rounded-full transition-colors relative ${
        checked ? 'bg-rs-gold' : 'bg-rs-border'
      }`}
    >
      <div className={`w-4 h-4 rounded-full bg-white absolute top-0.5 transition-transform ${
        checked ? 'translate-x-5' : 'translate-x-0.5'
      }`} />
    </button>
  )
}

export default function SettingsView({ accounts, onClose, onSettingsChanged }: Props) {
  const { theme, setTheme } = useTheme()
  const [settings, setSettings] = useState<Settings>(loadSettings)
  const [loggingOut, setLoggingOut] = useState(false)

  const update = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    updateSetting(key, value)
    setSettings({ ...settings, [key]: value })
  }

  const handleLogoutAll = async () => {
    setLoggingOut(true)
    try {
      await logout()
      onSettingsChanged()
    } catch (e) {
      console.error('Logout failed:', e)
    } finally {
      setLoggingOut(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div className="bg-rs-bg-light border border-rs-border rs-card w-[600px] max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="px-6 py-4 border-b border-rs-border flex items-center justify-between">
          <h2 className="text-lg font-bold text-rs-text">Settings</h2>
          <button
            onClick={onClose}
            aria-label="Close settings"
            className="w-8 h-8 flex items-center justify-center text-rs-muted hover:text-rs-text rounded transition-colors cursor-pointer"
          >
            <CloseIcon />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          <section>
            <h3 className={SECTION_TITLE}>Appearance</h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-rs-muted block mb-2">Theme</label>
                <div className="grid grid-cols-2 gap-2">
                  {themes.map((t) => (
                    <button
                      key={t.id}
                      onClick={() => setTheme(t.id)}
                      className={`px-4 py-3 rounded text-sm text-left transition-all ${
                        theme.id === t.id
                          ? 'bg-rs-gold/10 border border-rs-gold text-rs-gold'
                          : 'bg-rs-card border border-rs-border text-rs-text hover:border-rs-muted'
                      }`}
                    >
                      {t.name}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-rs-text">Disable Effects</div>
                  <div className="text-xs text-rs-muted">Disable special theme effects</div>
                </div>
                <Toggle checked={settings.disableEffects} onChange={() => update('disableEffects', !settings.disableEffects)} />
              </div>
            </div>
          </section>

          <section>
            <h3 className={SECTION_TITLE}>Behavior</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-rs-text">Close to System Tray</div>
                  <div className="text-xs text-rs-muted">Minimize to system tray instead of closing</div>
                </div>
                <Toggle checked={settings.closeToTray} onChange={() => update('closeToTray', !settings.closeToTray)} />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-rs-text">Close on Launch</div>
                  <div className="text-xs text-rs-muted">Close or hide window when launching a game</div>
                </div>
                <Toggle checked={settings.closeOnLaunch} onChange={() => update('closeOnLaunch', !settings.closeOnLaunch)} />
              </div>
            </div>
          </section>

          <section>
            <h3 className={SECTION_TITLE}>Accounts</h3>
            <div className="space-y-3">
              {accounts.length === 0 ? (
                <p className="text-xs text-rs-muted">No accounts added</p>
              ) : (
                accounts.map((account) => (
                  <div
                    key={account.username}
                    className="flex items-center justify-between px-4 py-3 bg-rs-card border border-rs-border rounded"
                  >
                    <div>
                      <div className="text-sm font-bold text-rs-text">{account.display_name || account.username}</div>
                      {account.email && (
                        <div className="text-xs text-rs-muted">{account.email}</div>
                      )}
                    </div>
                  </div>
                ))
              )}
              {accounts.length > 0 && (
                <button
                  onClick={handleLogoutAll}
                  disabled={loggingOut}
                  className="w-full py-3 px-4 text-sm text-rs-red border border-rs-red/30 rounded-md hover:bg-rs-red/10 transition-colors cursor-pointer disabled:opacity-50"
                >
                  {loggingOut ? 'Logging out...' : 'Logout All Accounts'}
                </button>
              )}
            </div>
          </section>

          <section>
            <h3 className={SECTION_TITLE}>About</h3>
            <div className="text-xs text-rs-muted space-y-1">
              <p>RS3TK</p>
              <p>RuneScape Third-party Client Launcher</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
