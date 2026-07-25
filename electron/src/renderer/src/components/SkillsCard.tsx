import { useState, useEffect, useRef, useMemo } from 'react'
import type { RuneMetrics, SkillValue } from '../types'
import { SKILL_NAMES } from '../types'
import { formatXpScaled, formatXp } from '../lib/format'

interface Props {
  metrics: RuneMetrics | null
}

function getColumns(width: number): number {
  if (width >= 500) return 6
  if (width >= 420) return 5
  if (width >= 340) return 4
  if (width >= 260) return 3
  return 2
}

export default function SkillsCard({ metrics }: Props) {
  const skillMap = useMemo(() => {
    const map = new Map<number, SkillValue>()
    metrics?.skill_values?.forEach(sv => map.set(sv.id, sv))
    return map
  }, [metrics])

  const containerRef = useRef<HTMLDivElement>(null)
  const [columns, setColumns] = useState(6)

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const observer = new ResizeObserver(([entry]) => {
      setColumns(getColumns(entry.contentRect.width))
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return (
    <div ref={containerRef} className="bg-rs-card border border-rs-border rs-card h-full flex flex-col">
      <div className="px-4 py-3 border-b border-rs-border flex items-center justify-between">
        <h2 className="text-xs font-bold text-rs-header tracking-wider">SKILL SUMMARY</h2>
        {metrics && (
          <span className="text-xs text-rs-muted">
            Total Level: {metrics.total_skill.toLocaleString()} • Total XP: {formatXp(metrics.total_xp)}
          </span>
        )}
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        <div
          className="grid gap-1"
          style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
        >
          {SKILL_NAMES.map((name, i) => {
            const sv = skillMap.get(i)
            return (
              <div
                key={name}
                className="flex items-center gap-1.5 px-1 py-1 bg-rs-card-hover border border-rs-border rs-card-sm h-[44px] hover:bg-rs-card-hover hover:border-rs-border transition-colors duration-150"
              >
                <img
                  src={`/skills/${name}.png`}
                  alt={name}
                  className="w-7 h-7 flex-shrink-0"
                />
                <div className="text-sm leading-tight min-w-0">
                  <div className="text-rs-gold truncate">{sv?.level ?? 1}</div>
                  <div className="text-rs-muted text-xs truncate">{sv ? formatXpScaled(sv.xp) : '0'}</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
