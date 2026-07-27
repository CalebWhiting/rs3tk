import { useState, useEffect, useRef, useMemo } from 'react'
import type { RuneMetrics } from '../types'
import { CARD_SHELL, CARD_HEADER, CARD_TITLE } from '../lib/styles'

interface Props {
  metrics: RuneMetrics | null
}

const COLORS = { complete: 'var(--rs-pie-complete)', started: 'var(--rs-pie-started)', notStarted: 'var(--rs-pie-not-started)' } as const
const RADIUS = 42.5
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

function PieChart({ data, total }: { data: { name: string; value: number; color: string }[]; total: number }) {
  let offset = 0

  return (
    <svg viewBox="0 0 100 100" className="w-full h-full">
      {total > 0 && data.map((segment) => {
        const arcLength = (segment.value / total) * CIRCUMFERENCE
        const dashOffset = -offset
        offset += arcLength

        return (
          <circle
            key={segment.name}
            cx="50"
            cy="50"
            r={RADIUS}
            fill="none"
            stroke={segment.color}
            strokeWidth="25"
            strokeDasharray={`${arcLength} ${CIRCUMFERENCE}`}
            strokeDashoffset={dashOffset}
            transform="rotate(-90 50 50)"
          />
        )
      })}
      {total === 0 && (
        <circle cx="50" cy="50" r={RADIUS} fill="none" stroke="var(--rs-card)" strokeWidth="25" />
      )}
    </svg>
  )
}

export default function QuestsCard({ metrics }: Props) {
  const qc = metrics?.quests_complete ?? 0
  const qs = metrics?.quests_started ?? 0
  const qn = metrics?.quests_not_started ?? 0
  const total = qc + qs + qn

  const data = useMemo(() => [
    { name: 'Complete', value: qc, color: COLORS.complete },
    { name: 'Started', value: qs, color: COLORS.started },
    { name: 'Not Started', value: qn, color: COLORS.notStarted },
  ], [qc, qs, qn])

  const containerRef = useRef<HTMLDivElement>(null)
  const [showChart, setShowChart] = useState(true)

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const observer = new ResizeObserver(([entry]) => {
      setShowChart(entry.contentRect.width >= 280)
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return (
    <div ref={containerRef} className={CARD_SHELL}>
      <div className={CARD_HEADER}>
        <h2 className={CARD_TITLE}>QUESTS</h2>
      </div>
      <div className="p-4">
        <div className={`flex items-center ${showChart ? 'justify-center gap-8' : 'justify-center'}`}>
          {showChart && (
            <div className="w-[120px] h-[120px] flex-shrink-0">
              <PieChart data={data} total={total} />
            </div>
          )}
          <div className="space-y-3">
            {data.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                <span className="text-rs-muted text-sm">{item.name}</span>
                <span className="text-rs-text text-sm font-bold ml-auto">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="mt-4 pt-3 border-t border-rs-border flex justify-between">
          <span className="text-rs-muted text-sm">Total</span>
          <span className="text-rs-text text-sm font-bold">{total}</span>
        </div>
      </div>
    </div>
  )
}
