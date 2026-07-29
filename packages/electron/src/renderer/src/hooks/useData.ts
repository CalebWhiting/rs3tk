import { useState, useEffect, useCallback, useRef } from 'react'
import type { Character, CharactersResponse, Account, Client, RuneMetrics } from '../types'

/** Hook template for a one-shot fetch on mount, plus a manual refetch. */
function useFetcher<T>(fetcher: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const alive = useRef(true)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetcher()
      if (alive.current) setData(result)
    } catch (e) {
      if (alive.current) setError(e instanceof Error ? e.message : 'Fetch failed')
    } finally {
      if (alive.current) setLoading(false)
    }
  }, [fetcher])

  useEffect(() => {
    alive.current = true
    void refetch()
    return () => { alive.current = false }
  }, [refetch])

  return { data, loading, error, refetch }
}

export function useCharacters() {
  const fetcher = useCallback(() => window.api.getCharacters(), [])
  const { data, loading, error, refetch } = useFetcher<CharactersResponse>(fetcher)
  return {
    data: data?.characters ?? [],
    authErrors: data?.auth_errors ?? [],
    loading,
    error,
    refetch,
  }
}

export function useAccounts() {
  const fetcher = useCallback(() => window.api.getAccounts(), [])
  const { data, loading, error, refetch } = useFetcher<Account[]>(fetcher)
  return { data: data ?? [], loading, error, refetch }
}

export function useClients() {
  const fetcher = useCallback(() => window.api.getClients(), [])
  const { data, loading, error, refetch } = useFetcher<Client[]>(fetcher)
  return { data: data ?? [], loading, error, refetch }
}

export function useMetrics(characterName: string | null) {
  const fetcher = useCallback(() => {
    if (!characterName) return Promise.reject(new Error('no character'))
    return window.api.getMetrics(characterName)
  }, [characterName])
  const { data, loading, error, refetch } = useFetcher<RuneMetrics>(fetcher)
  return { data, loading, error, refetch }
}

export async function login(systemBrowser = false): Promise<{ username: string; account_count: number }> {
  return window.api.login(systemBrowser)
}

export async function logout(username?: string): Promise<void> {
  await window.api.logout(username)
}

export async function launchGame(clientKey: string, character: string): Promise<void> {
  await window.api.launchGame(clientKey, character)
}

export async function installClient(clientKey: string): Promise<string> {
  const result = await window.api.installClient(clientKey)
  return result.message
}
