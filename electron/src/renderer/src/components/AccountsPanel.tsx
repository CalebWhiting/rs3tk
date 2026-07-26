import { memo } from 'react'
import type { Character, Account } from '../types'
import { RefreshIcon } from './icons'
import { PANEL_SIDEBAR, CARD_HEADER, CARD_TITLE } from '../lib/styles'

interface Props {
  accounts: Account[]
  characters: Character[]
  selectedCharacter: string | null
  onSelectCharacter: (name: string) => void
  onAddAccount: () => void
  onLogout: (username: string) => void
  onRefresh: () => void
}

function avatarCdnUrl(name: string): string {
  return `https://secure.runescape.com/m=avatar-rs/${encodeURIComponent(name)}/chat.png`
}

export default memo(function AccountsPanel({ accounts, characters, selectedCharacter, onSelectCharacter, onAddAccount, onLogout, onRefresh }: Props) {
  return (
    <div className={PANEL_SIDEBAR}>
      <div className={CARD_HEADER}>
        <h2 className={CARD_TITLE}>ACCOUNTS & CHARACTERS</h2>
      </div>
      <div className="flex-1 overflow-y-auto">
        {accounts.map((account) => {
          const accountChars = characters.filter(c => c.username === account.username)
          return (
            <div key={account.username}>
              <div className="px-4 py-2 flex items-center justify-between group">
                <div className="min-w-0">
                  <div className="text-sm font-bold text-rs-text truncate">{account.display_name || account.username}</div>
                  {account.email && (
                    <div className="text-xs text-rs-muted truncate">{account.email}</div>
                  )}
                </div>
                <button
                  onClick={() => onLogout(account.username)}
                  className="text-rs-muted hover:text-rs-red text-[10px] opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer flex-shrink-0 ml-2"
                >
                  Logout
                </button>
              </div>
              {accountChars.map((char) => (
                <button
                  key={char.display_name}
                  onClick={() => onSelectCharacter(char.display_name)}
                  className={`w-full flex items-center gap-3 px-4 py-2 transition-all duration-150 cursor-pointer ${
                    selectedCharacter === char.display_name
                      ? 'bg-rs-card-hover border-l-2 border-l-rs-gold'
                      : 'hover:bg-rs-card-hover border-l-2 border-l-transparent'
                  }`}
                >
                  <div className="w-8 h-8 rounded-full bg-rs-card flex-shrink-0 overflow-hidden">
                    <img
                      src={avatarCdnUrl(char.display_name)}
                      alt=""
                      className="w-full h-full object-cover"
                      onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                    />
                  </div>
                  <div className="flex-1 text-left min-w-0">
                    <div className="text-sm font-bold text-rs-text flex items-center gap-1">
                      {char.display_name}
                      {char.is_member && <span className="text-rs-gold text-[11px] member-symbol"></span>}
                    </div>
                    {char.is_member && (
                      <div className="text-[11px] text-rs-green">Member</div>
                    )}
                  </div>
                  {selectedCharacter === char.display_name && (
                    <div
                      role="button"
                      tabIndex={0}
                      onClick={(e) => { e.stopPropagation(); onRefresh() }}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.stopPropagation(); onRefresh() } }}
                      className="w-5 h-5 rounded-full bg-rs-gold flex items-center justify-center shadow-[0_0_8px_var(--rs-gold)] text-rs-btn-text hover:brightness-110 transition-all flex-shrink-0 cursor-pointer"
                    >
                      <RefreshIcon />
                    </div>
                  )}
                </button>
              ))}
            </div>
          )
        })}
      </div>
      <div className="p-4">
        <button
          onClick={onAddAccount}
          className="gold-button w-full"
        >
          + Add Jagex Account
        </button>
      </div>
    </div>
  )
})
