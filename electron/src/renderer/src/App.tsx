import { useState, useEffect, useCallback, useRef } from 'react'
import TitleBar from './components/TitleBar'
import AccountsPanel from './components/AccountsPanel'
import AuthBanner from './components/AuthBanner'
import Dashboard from './components/Dashboard'
import ClientPanel from './components/ClientPanel'
import BottomBar from './components/BottomBar'
import LoadingOverlay from './components/LoadingOverlay'
import NoiseBackground from './components/NoiseBackground'
import SettingsView from './components/SettingsView'
import { useCharacters, useAccounts, useClients, useMetrics, login, logout } from './hooks/useData'
import { initSettings } from './lib/settings'

function App() {
  const { data: characters, authErrors, loading: loadingChars, refetch: refetchChars } = useCharacters()
  const { data: accounts, loading: loadingAccounts, refetch: refetchAccounts } = useAccounts()
  const { data: clients, loading: loadingClients } = useClients()
  const [selectedCharacter, setSelectedCharacter] = useState<string | null>(null)
  const [selectedClient, setSelectedClient] = useState(() => {
    try { return localStorage.getItem('rs3tk-selected-client') || 'official' } catch { return 'official' }
  })
  const [showSettings, setShowSettings] = useState(false)
  const [authBannerDismissed, setAuthBannerDismissed] = useState(false)

  const charactersRef = useRef(characters)
  charactersRef.current = characters

  useEffect(() => {
    initSettings()
  }, [])

  useEffect(() => {
    try {
      localStorage.setItem('rs3tk-selected-client', selectedClient)
      window.api.setPersistentSettings({ selectedClient })
    } catch {}
  }, [selectedClient])

  useEffect(() => {
    window.api.getPersistentSettings().then((settings) => {
      if (settings.selectedClient && typeof settings.selectedClient === 'string') {
        setSelectedClient(settings.selectedClient)
      }
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (characters.length > 0 && !selectedCharacter) {
      setSelectedCharacter(characters[0].display_name)
    } else if (characters.length === 0 && selectedCharacter) {
      setSelectedCharacter(null)
    }
  }, [characters, selectedCharacter])

  const { data: metrics, loading: loadingMetrics, refetch: refetchMetrics } = useMetrics(selectedCharacter)

  const handleRefresh = useCallback(() => {
    if (selectedCharacter) refetchMetrics()
  }, [selectedCharacter, refetchMetrics])

  const handleAddAccount = useCallback(async () => {
    try {
      await login()
      refetchChars()
      refetchAccounts()
    } catch (e) {
      console.error('Login failed:', e)
    }
  }, [refetchChars, refetchAccounts])

  const handleLogout = useCallback(async (username: string) => {
    try {
      await logout(username)
      refetchChars()
      refetchAccounts()
      const remaining = charactersRef.current.filter(c => c.username !== username)
      setSelectedCharacter(remaining.length > 0 ? remaining[0].display_name : null)
    } catch (e) {
      console.error('Logout failed:', e)
    }
  }, [refetchChars, refetchAccounts])

  const handleOpenSettings = useCallback(() => setShowSettings(true), [])
  const handleCloseSettings = useCallback(() => setShowSettings(false), [])
  const handleSettingsChanged = useCallback(() => {
    refetchChars()
    refetchAccounts()
    setSelectedCharacter(null)
  }, [refetchChars, refetchAccounts])

  const handleAuthLogin = useCallback(async () => {
    try {
      await login()
      setAuthBannerDismissed(false)
      refetchChars()
      refetchAccounts()
    } catch (e) {
      console.error('Login failed:', e)
    }
  }, [refetchChars, refetchAccounts])

  const visibleAuthErrors = authBannerDismissed ? [] : authErrors

  return (
    <NoiseBackground>
      <div className="h-screen flex flex-col border border-rs-border">
        <TitleBar onSettings={handleOpenSettings} />
        <AuthBanner
          errors={visibleAuthErrors}
          onLogin={handleAuthLogin}
          onDismiss={() => setAuthBannerDismissed(true)}
        />
        <div className="flex-1 flex gap-3 p-3 overflow-hidden min-w-0">
          <AccountsPanel
            accounts={accounts}
            characters={characters}
            selectedCharacter={selectedCharacter}
            onSelectCharacter={setSelectedCharacter}
            onAddAccount={handleAddAccount}
            onLogout={handleLogout}
            onRefresh={handleRefresh}
          />
          <Dashboard
            characterName={selectedCharacter}
            metrics={metrics}
            loadingMetrics={loadingMetrics}
          />
          <ClientPanel
            clients={clients}
            selectedClient={selectedClient}
            onSelectClient={setSelectedClient}
            selectedCharacter={selectedCharacter}
          />
        </div>
        <BottomBar selectedClient={selectedClient} />
        <LoadingOverlay visible={loadingChars || loadingAccounts || loadingClients} />
      </div>
      {showSettings && <SettingsView accounts={accounts} onClose={handleCloseSettings} onSettingsChanged={handleSettingsChanged} />}
    </NoiseBackground>
  )
}

export default App
