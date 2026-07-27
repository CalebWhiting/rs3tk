import { useState, useEffect, useCallback, useRef } from 'react'
import type { Character, CharactersResponse, Account, Client, RuneMetrics } from '../types'

const BACKEND_STARTUP_RETRIES = 15
const BACKEND_STARTUP_BASE_DELAY = 500

function useApi<T>(endpoint: string, errorMsg: string) {
  const [data, setData] = useState<T>([] as T)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const ignore = useRef(false)
  const retryTimer = useRef<ReturnType<typeof setTimeout>>(undefined)

  const refetch = useCallback(async (attempt = 0) => {
    setLoading(true)
    setError(null)
    try {
      const result = await window.api.callBackend(endpoint)
      if (!ignore.current) {
        if (result.error) throw new Error(result.error)
        setData(result)
      }
    } catch (e) {
      if (ignore.current) return
      const msg = e instanceof Error ? e.message : errorMsg
      if (msg === 'Backend not available' && attempt < BACKEND_STARTUP_RETRIES) {
        const delay = Math.min(BACKEND_STARTUP_BASE_DELAY * Math.pow(1.5, attempt), 5000)
        retryTimer.current = setTimeout(() => refetch(attempt + 1), delay)
        return
      }
      setError(msg)
    } finally {
      if (!ignore.current) setLoading(false)
    }
  }, [endpoint, errorMsg])

  useEffect(() => {
    ignore.current = false
    refetch()
    return () => { ignore.current = true; clearTimeout(retryTimer.current) }
  }, [refetch])

  return { data, loading, error, refetch }
}

export function useCharacters() {
  const [data, setData] = useState<Character[]>([])
  const [authErrors, setAuthErrors] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const ignore = useRef(false)
  const retryTimer = useRef<ReturnType<typeof setTimeout>>(undefined)

  const refetch = useCallback(async (attempt = 0) => {
    setLoading(true)
    setError(null)
    try {
      const result: CharactersResponse = await window.api.callBackend('/api/characters')
      if (!ignore.current) {
        if (result.error) throw new Error(result.error)
        setData(result.characters ?? [])
        setAuthErrors(result.auth_errors ?? [])
      }
    } catch (e) {
      if (ignore.current) return
      const msg = e instanceof Error ? e.message : 'Failed to load characters'
      if (msg === 'Backend not available' && attempt < BACKEND_STARTUP_RETRIES) {
        const delay = Math.min(BACKEND_STARTUP_BASE_DELAY * Math.pow(1.5, attempt), 5000)
        retryTimer.current = setTimeout(() => refetch(attempt + 1), delay)
        return
      }
      setError(msg)
    } finally {
      if (!ignore.current) setLoading(false)
    }
  }, [])

  useEffect(() => {
    ignore.current = false
    refetch()
    return () => { ignore.current = true; clearTimeout(retryTimer.current) }
  }, [refetch])

  return { data, authErrors, loading, error, refetch }
}

export function useAccounts() {
  return useApi<Account[]>('/api/accounts', 'Failed to load accounts')
}

export function useClients() {
  return useApi<Client[]>('/api/clients', 'Failed to load clients')
}

export function useMetrics(characterName: string | null) {
  const [data, setData] = useState<RuneMetrics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const ignore = useRef(false)
  const retryTimer = useRef<ReturnType<typeof setTimeout>>(undefined)

  const refetch = useCallback(async (attempt = 0) => {
    if (!characterName) return
    setLoading(true)
    setError(null)
    try {
      const result = await window.api.callBackend(`/api/metrics/${encodeURIComponent(characterName)}`)
      if (!ignore.current) {
        if (result.error) throw new Error(result.error)
        setData(result)
      }
    } catch (e) {
      if (ignore.current) return
      const msg = e instanceof Error ? e.message : 'Failed to load metrics'
      if (msg === 'Backend not available' && attempt < BACKEND_STARTUP_RETRIES) {
        const delay = Math.min(BACKEND_STARTUP_BASE_DELAY * Math.pow(1.5, attempt), 5000)
        retryTimer.current = setTimeout(() => refetch(attempt + 1), delay)
        return
      }
      setError(msg)
    } finally {
      if (!ignore.current) setLoading(false)
    }
  }, [characterName])

  useEffect(() => {
    ignore.current = false
    refetch()
    return () => { ignore.current = true; clearTimeout(retryTimer.current) }
  }, [refetch])

  return { data, loading, error, refetch }
}

export async function login(systemBrowser = false): Promise<{ username: string; account_count: number }> {
  const result = await window.api.callBackendPost('/api/login', { system_browser: systemBrowser })
  if (result.error) throw new Error(result.error)
  return result
}

export async function logout(username?: string): Promise<void> {
  const result = await window.api.callBackendPost('/api/logout', username ? { username } : {})
  if (result.error) throw new Error(result.error)
}

export async function launchGame(clientKey: string, character: string): Promise<void> {
  const result = await window.api.callBackendPost('/api/launch', { client_key: clientKey, character })
  if (result.error) throw new Error(result.error)
}

export async function installClient(clientKey: string): Promise<string> {
  const result = await window.api.callBackendPost('/api/install', { client_key: clientKey })
  if (result.error) throw new Error(result.error)
  return result.message ?? 'Installed'
}
