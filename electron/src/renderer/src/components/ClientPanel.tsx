import { useState } from 'react'
import type { Client } from '../types'
import { launchGame } from '../hooks/useData'

interface Props {
  clients: Client[]
  selectedClient: string
  onSelectClient: (key: string) => void
  selectedCharacter: string | null
}

export default function ClientPanel({ clients, selectedClient, onSelectClient, selectedCharacter }: Props) {
  const [launchError, setLaunchError] = useState<string | null>(null)

  const handleLaunch = async () => {
    if (!selectedCharacter) return
    setLaunchError(null)
    try {
      await launchGame(selectedClient, selectedCharacter)
      window.api.launchGame()
    } catch (e) {
      setLaunchError(e instanceof Error ? e.message : 'Failed to launch')
    }
  }

  return (
    <div className="w-[260px] flex-shrink-0 bg-rs-card border border-rs-border rs-card flex flex-col">
      <div className="px-4 py-3 border-b border-rs-border">
        <h2 className="text-xs font-bold text-rs-header tracking-wider">SELECT CLIENT</h2>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {clients.map((client) => (
          <button
            key={client.key}
            onClick={() => onSelectClient(client.key)}
            className={`w-full h-16 flex items-center gap-4 px-3 py-2 rs-card border transition-colors ${
              selectedClient === client.key
                ? 'border-rs-gold bg-rs-gold/5'
                : 'border-rs-border bg-transparent hover:border-rs-muted'
            }`}
          >
            <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center">
              <img src={`/clients/${client.key}.png`} alt={client.name} className="w-9 h-9" />
            </div>
            <div className="flex-1 text-left">
              <div className="text-sm font-bold text-rs-text">{client.name}</div>
              <div className={`text-xs ${client.installed ? 'text-rs-green' : 'text-rs-muted'}`}>
                {client.installed ? 'Installed' : 'Not installed'}
              </div>
            </div>
            {selectedClient === client.key && (
              <div className="w-6 h-6 rounded-full bg-rs-gold flex items-center justify-center shadow-[0_0_8px_var(--rs-gold)]">
                <span className="text-rs-btn-text text-xs font-bold">✓</span>
              </div>
            )}
          </button>
        ))}
      </div>
      <div className="p-4">
        <div className="flex mx-2">
          <button
            onClick={handleLaunch}
            disabled={!selectedCharacter}
            className="gold-button gold-button-split-left flex-1 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            PLAY NOW
          </button>
          <button
            disabled={!selectedCharacter}
            className="gold-button gold-button-split-right px-3 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M6 9l6 6 6-6"/></svg>
          </button>
        </div>
        {launchError && (
          <div className="mt-2 text-xs text-rs-red text-center truncate">{launchError}</div>
        )}
      </div>
    </div>
  )
}
