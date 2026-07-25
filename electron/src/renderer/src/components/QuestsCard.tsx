import { useState, useEffect, useRef, useMemo } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import type { RuneMetrics } from '../types'

interface Props {
  metrics: RuneMetrics | null
}

const COLORS = { complete: 'var(--rs-pie-complete)', started: 'var(--rs-pie-started)', notStarted: 'var(--rs-pie-not-started)' } as const

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

  const pieData = useMemo(() => total > 0 ? data : [{ name: 'Empty', value: 1, color: 'var(--rs-card)' }], [data, total])

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
    <div ref={containerRef} className="bg-rs-card border border-rs-border rs-card h-full">
      <div className="px-4 py-3 border-b border-rs-border">
        <h2 className="text-xs font-bold text-rs-header tracking-wider">QUESTS</h2>
      </div>
      <div className="p-4">
        <div className={`flex items-center ${showChart ? 'justify-center gap-8' : 'justify-center'}`}>
          {showChart && (
            <div className="w-[120px] h-[120px] rounded-full border-[3px] border-rs-bg overflow-hidden flex-shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={30}
                    outerRadius={55}
                    dataKey="value"
                    startAngle={90}
                    endAngle={-270}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
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
