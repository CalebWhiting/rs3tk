import type { Character, RuneMetrics, Account, Client } from '../renderer/src/types'

/** Typed surface for the renderer ↔ bridge IPC.
 *
 * Each method maps 1:1 to a Python bridge handler. Drift between this
 * file and the bridge's `METHODS` dict is caught at runtime: a missing
 * Python method returns `{ error: "Unknown method: foo" }`, which the
 * main process turns into a rejected IPC call. The cross-module smoke
 * test in `tests/test_bridge_roundtrip.py` exercises every method and
 * asserts the JSON shape matches these types.
 */
export interface BridgeAPI {
  getCharacters(): Promise<{ characters: Character[]; auth_errors: string[] }>
  getAccounts(): Promise<Account[]>
  getClients(): Promise<Client[]>
  getStatus(): Promise<{ status: string }>
  getMetrics(name: string): Promise<RuneMetrics>
  login(systemBrowser?: boolean): Promise<{ username: string; account_count: number }>
  logout(username?: string, all?: boolean): Promise<{ status: string }>
  launchGame(clientKey: string, character: string): Promise<{ status: string }>
  installClient(clientKey: string): Promise<{ status: string; message: string }>
}
