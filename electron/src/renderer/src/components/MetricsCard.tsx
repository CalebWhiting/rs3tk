import { useState, useEffect, useRef } from 'react'
import type { RuneMetrics } from '../types'
import { SKILL_NAMES } from '../types'
import { formatXpScaled, formatXp } from '../lib/format'

interface Props {
  metrics: RuneMetrics | null
}

export default function MetricsCard({ metrics }: Props) {
  const m = metrics
  const containerRef = useRef<HTMLDivElement>(null)
  const [narrow, setNarrow] = useState(false)

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const observer = new ResizeObserver(([entry]) => {
      setNarrow(entry.contentRect.width < 335)
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return (
    <div ref={containerRef} className="bg-rs-card border border-rs-border rs-card h-full">
      <div className="px-4 py-3 border-b border-rs-border">
        <h2 className="text-xs font-bold text-rs-header tracking-wider">METRICS</h2>
      </div>
      <div className="flex flex-col divide-y divide-rs-divider border-b border-rs-divider">
        {narrow ? (
          <>
            <MetricCell label="Overall Rank" value={m?.rank || 'N/A'} />
            <MetricCell label="Combat Level" value={m?.combat_level?.toString() || 'N/A'} />
            <MetricCell label="Total Level" value={m?.total_skill?.toString() || 'N/A'} />
            <LowestSkillCell metrics={m} />
            <HighestSkillCell metrics={m} />
            <MetricCell label="Total XP" value={m ? formatXp(m.total_xp) : 'N/A'} />
            <MetricCell label="Quests Complete" value={m?.quests_complete?.toString() || 'N/A'} />
            <MetricCell
              label="Quests Missing"
              value={m ? (m.quests_not_started + m.quests_started).toString() : 'N/A'}
            />
          </>
        ) : (
          <>
            <div className="grid grid-cols-3 divide-x divide-rs-divider">
              <MetricCell label="Overall Rank" value={m?.rank || 'N/A'} />
              <MetricCell label="Combat Level" value={m?.combat_level?.toString() || 'N/A'} />
              <MetricCell label="Total Level" value={m?.total_skill?.toString() || 'N/A'} />
            </div>
            <div className="grid grid-cols-2 divide-x divide-rs-divider">
              <LowestSkillCell metrics={m} />
              <HighestSkillCell metrics={m} />
            </div>
            <div className="grid grid-cols-3 divide-x divide-rs-divider">
              <MetricCell label="Total XP" value={m ? formatXp(m.total_xp) : 'N/A'} />
              <MetricCell label="Quests Complete" value={m?.quests_complete?.toString() || 'N/A'} />
              <MetricCell
                label="Quests Missing"
                value={m ? (m.quests_not_started + m.quests_started).toString() : 'N/A'}
              />
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function MetricCell({ label, value, icon }: { label: string; value: string; icon?: string }) {
  return (
    <div className="px-3 py-2.5 bg-transparent flex items-center justify-between">
      <div className="min-w-0">
        <div className="text-[11px] text-rs-muted font-mono truncate">{label}</div>
        <div className="text-base font-bold text-rs-text font-mono truncate">{value}</div>
      </div>
      {icon && (
        <img src={`/skills/${icon}.png`} alt={icon} className="w-6 h-6 flex-shrink-0" />
      )}
    </div>
  )
}

function LowestSkillCell({ metrics }: { metrics: RuneMetrics | null }) {
  if (!metrics?.skill_values?.length) {
    return <MetricCell label="Lowest Skill" value="N/A" />
  }
  const lowest = metrics.skill_values.reduce((min, s) =>
    s.level < min.level || (s.level === min.level && s.xp < min.xp) ? s : min
  , metrics.skill_values[0])
  const name = lowest.id < SKILL_NAMES.length ? SKILL_NAMES[lowest.id] : undefined
  return <MetricCell label="Lowest Skill" value={`${lowest.level} (${formatXpScaled(lowest.xp)})`} icon={name} />
}

function HighestSkillCell({ metrics }: { metrics: RuneMetrics | null }) {
  if (!metrics?.skill_values?.length) {
    return <MetricCell label="Highest Skill" value="N/A" />
  }
  const highest = metrics.skill_values.reduce((max, s) => s.level > max.level ? s : max, metrics.skill_values[0])
  const capped = Math.min(highest.xp, 2_000_000_000)
  const name = highest.id < SKILL_NAMES.length ? SKILL_NAMES[highest.id] : undefined
  return <MetricCell label="Highest Skill" value={`${highest.level} (${formatXpScaled(capped)})`} icon={name} />
}
