import { useState } from 'react'
import { CloseIcon } from './icons'

interface Props {
  errors: string[]
  onLogin: () => void
  onDismiss: () => void
}

export default function AuthBanner({ errors, onLogin, onDismiss }: Props) {
  const [expanded, setExpanded] = useState(false)

  if (errors.length === 0) return null

  const summary = errors.length === 1
    ? errors[0]
    : `${errors.length} accounts need re-login`

  return (
    <div className="mx-3 mb-3 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-4 py-3">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <span className="text-yellow-400 text-lg flex-shrink-0">⚠</span>
          <span className="text-sm text-rs-text truncate">{summary}</span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {errors.length > 1 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs text-rs-muted hover:text-rs-text transition-colors cursor-pointer"
            >
              {expanded ? 'Less' : 'Details'}
            </button>
          )}
          <button
            onClick={onLogin}
            className="px-3 py-1 text-xs font-bold rounded bg-yellow-500/20 text-yellow-300 hover:bg-yellow-500/30 transition-colors cursor-pointer"
          >
            Re-login
          </button>
          <button
            onClick={onDismiss}
            className="text-rs-muted hover:text-rs-text transition-colors cursor-pointer"
            aria-label="Dismiss"
          >
            <CloseIcon size={12} />
          </button>
        </div>
      </div>
      {expanded && errors.length > 1 && (
        <div className="mt-2 pl-7 space-y-1">
          {errors.map((err, i) => (
            <div key={i} className="text-xs text-rs-muted">{err}</div>
          ))}
        </div>
      )}
    </div>
  )
}
