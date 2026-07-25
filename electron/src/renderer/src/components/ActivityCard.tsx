import { useState, useEffect, useRef } from 'react'
import type { RuneMetrics } from '../types'

interface Props {
  metrics: RuneMetrics | null
}

export default function ActivityCard({ metrics }: Props) {
  const allActivities = metrics?.activities ?? []
  const containerRef = useRef<HTMLDivElement>(null)
  const [maxItems, setMaxItems] = useState(5)

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const observer = new ResizeObserver(([entry]) => {
      const w = entry.contentRect.width
      if (w < 200) setMaxItems(2)
      else if (w < 300) setMaxItems(3)
      else setMaxItems(5)
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  const activities = allActivities.slice(0, maxItems)

  return (
    <div ref={containerRef} className="bg-rs-card border border-rs-border rs-card h-full flex flex-col">
      <div className="px-4 py-3 border-b border-rs-border">
        <h2 className="text-xs font-bold text-rs-header tracking-wider">RECENT ACTIVITY</h2>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        {activities.length === 0 ? (
          <div className="text-rs-muted text-sm">No recent activity</div>
        ) : (
          <div className="space-y-3">
            {activities.map((act, i) => (
              <div key={i} className="flex gap-3 px-2 py-1.5 -mx-2 rounded hover:bg-rs-card-hover transition-colors duration-150">
                <div className="w-5 h-5 flex-shrink-0 flex items-center justify-center text-rs-gold text-base">
                  •
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-rs-muted">{act.date}</div>
                  <div className="text-sm text-rs-text break-words">{act.text}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
