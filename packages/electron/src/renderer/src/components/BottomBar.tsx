import { useState, useEffect, useRef } from 'react'

interface Props {
  selectedClient: string
}

export default function BottomBar({ selectedClient }: Props) {
  const [version, setVersion] = useState('')
  const [statusOk, setStatusOk] = useState<boolean | null>(null)
  const ignoreRef = useRef(false)

  useEffect(() => {
    ignoreRef.current = false
    window.api.getVersion().then(setVersion).catch(() => {})

    window.api.getStatus()
      .then(() => { if (!ignoreRef.current) setStatusOk(true) })
      .catch(() => { if (!ignoreRef.current) setStatusOk(false) })

    return () => { ignoreRef.current = true }
  }, [])

  const isOsrsClient = ['official', 'runelite', 'hdos'].includes(selectedClient)
  const newsUrl = isOsrsClient
    ? 'https://secure.runescape.com/m=news/archive?oldschool=1'
    : 'https://secure.runescape.com/m=news/list'

  const statusColor = statusOk === null ? 'text-rs-muted' : statusOk ? 'text-rs-green' : 'text-rs-yellow'
  const statusDot = statusOk === null ? 'bg-rs-muted' : statusOk ? 'bg-rs-green' : 'bg-rs-yellow'
  const statusText = statusOk === null ? 'Checking...' : statusOk ? 'All systems operational' : 'Status unknown'

  return (
    <div className="h-10 flex items-center justify-between px-6 border-t border-rs-border bg-rs-card">
      <div className="flex items-center gap-4">
        {version && <span className="text-rs-muted text-sm">v{version}</span>}
        <span className={`text-xs flex items-center gap-1.5 ${statusColor}`}>
          <span className="relative flex h-2 w-2">
            {statusOk === null && <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${statusDot}`} />}
            <span className={`relative inline-flex rounded-full h-2 w-2 ${statusDot}`} />
          </span>
          {statusText}
        </span>
      </div>
      <div className="flex items-center gap-4">
        <a href="https://discord.gg/torm-828918474784768010" target="_blank" rel="noopener noreferrer" className="text-rs-muted hover:text-rs-gold text-sm">Join Discord</a>
        <span className="text-rs-muted">|</span>
        <a href={newsUrl} target="_blank" rel="noopener noreferrer" className="text-rs-muted hover:text-rs-gold text-sm">RuneScape News</a>
      </div>
    </div>
  )
}
