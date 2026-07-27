import { useState } from 'react'
import type { Client } from '../types'
import { launchGame, installClient } from '../hooks/useData'
import { ChevronDownIcon } from './icons'
import { PANEL_SIDEBAR, CARD_HEADER, CARD_TITLE } from '../lib/styles'

interface Props {
  clients: Client[]
  selectedClient: string
  onSelectClient: (key: string) => void
  selectedCharacter: string | null
  onInstalled: () => void
}

export default function ClientPanel({ clients, selectedClient, onSelectClient, selectedCharacter, onInstalled }: Props) {
  const [launchError, setLaunchError] = useState<string | null>(null)
  const [installing, setInstalling] = useState<string | null>(null)
  const [installError, setInstallError] = useState<string | null>(null)

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

  const handleInstall = async (clientKey: string) => {
    setInstalling(clientKey)
    setInstallError(null)
    try {
      await installClient(clientKey)
      onInstalled()
    } catch (e) {
      setInstallError(e instanceof Error ? e.message : 'Failed to install')
    } finally {
      setInstalling(null)
    }
  }

  return (
    <div className={PANEL_SIDEBAR}>
      <div className={CARD_HEADER}>
        <h2 className={CARD_TITLE}>SELECT CLIENT</h2>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {clients.map((client) => (
          <button
            key={client.key}
            onClick={() => onSelectClient(client.key)}
            className={`w-full flex items-center gap-4 px-3 py-2 rs-card border transition-colors ${
              selectedClient === client.key
                ? 'border-rs-gold bg-rs-gold/5'
                : 'border-rs-border bg-transparent hover:border-rs-muted'
            }`}
          >
            <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center">
              <img src={`clients/${client.key}.png`} alt={client.name} className="w-9 h-9" />
            </div>
            <div className="flex-1 text-left">
              <div className="text-sm font-bold text-rs-text">{client.name}</div>
              <div className={`text-xs ${client.installed ? 'text-rs-green' : 'text-rs-muted'}`}>
                {installing === client.key
                  ? 'Installing...'
                  : client.installed
                    ? 'Installed'
                    : 'Not installed'}
              </div>
            </div>
            {client.installed ? (
              selectedClient === client.key && (
                <div className="w-6 h-6 rounded-full bg-rs-gold flex items-center justify-center shadow-[0_0_8px_var(--rs-gold)]">
                  <span className="text-rs-btn-text text-xs font-bold">✓</span>
                </div>
              )
            ) : (
              <button
                onClick={(e) => { e.stopPropagation(); handleInstall(client.key) }}
                disabled={installing !== null}
                className="px-2 py-1 text-xs font-bold rounded bg-rs-gold/20 text-rs-gold hover:bg-rs-gold/30 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {installing === client.key ? '...' : 'Install'}
              </button>
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
            <ChevronDownIcon />
          </button>
        </div>
        {(launchError || installError) && (
          <div className="mt-2 text-xs text-rs-red text-center truncate">
            {launchError || installError}
          </div>
        )}
      </div>
    </div>
  )
}
