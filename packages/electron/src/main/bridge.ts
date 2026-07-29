import { ChildProcess, spawn } from 'child_process'

type Pending = { resolve: (v: unknown) => void; reject: (e: Error) => void }

/** Stdio JSON-RPC client for the rs3tk-bridge Python child process. */
export class Bridge {
  private child: ChildProcess | null = null
  private nextId = 1
  private pending = new Map<number, Pending>()
  private buffer = ''

  start(command: string, args: string[]): void {
    this.child = spawn(command, args, { stdio: ['pipe', 'pipe', 'pipe'] })
    this.child.stdout?.setEncoding('utf-8')
    this.child.stdout?.on('data', (chunk: string) => this.onStdout(chunk))
    this.child.stderr?.on('data', (d) => console.error(`[bridge] ${d.toString().trim()}`))
    this.child.on('exit', (code) => {
      const err = new Error(`bridge exited with code ${code}`)
      for (const { reject } of this.pending.values()) reject(err)
      this.pending.clear()
      this.child = null
    })
  }

  call<T = unknown>(method: string, params: Record<string, unknown> = {}): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      if (!this.child?.stdin?.writable) return reject(new Error('bridge not running'))
      const id = this.nextId++
      this.pending.set(id, { resolve: resolve as (v: unknown) => void, reject })
      this.child.stdin.write(JSON.stringify({ id, method, params }) + '\n')
    })
  }

  stop(): void {
    this.child?.kill()
    this.child = null
  }

  isRunning(): boolean {
    return this.child !== null
  }

  private onStdout(chunk: string): void {
    this.buffer += chunk
    let nl: number
    while ((nl = this.buffer.indexOf('\n')) !== -1) {
      const line = this.buffer.slice(0, nl)
      this.buffer = this.buffer.slice(nl + 1)
      if (!line.trim()) continue
      try {
        const msg = JSON.parse(line)
        if (msg.id !== undefined && this.pending.has(msg.id)) {
          const { resolve, reject } = this.pending.get(msg.id)!
          this.pending.delete(msg.id)
          msg.error ? reject(new Error(msg.error.message ?? 'bridge error')) : resolve(msg.result)
        }
      } catch (e) {
        console.error('[bridge] malformed line:', line, e)
      }
    }
  }
}
