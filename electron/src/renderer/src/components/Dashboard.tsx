import { useState, useEffect, useRef, useCallback } from 'react'
import CharacterHeader from './CharacterHeader'
import MetricsCard from './MetricsCard'
import QuestsCard from './QuestsCard'
import ActivityCard from './ActivityCard'
import SkillsCard from './SkillsCard'
import LoadingOverlay from './LoadingOverlay'
import type { RuneMetrics } from '../types'

interface Props {
  characterName: string | null
  metrics: RuneMetrics | null
  loadingMetrics: boolean
}

export default function Dashboard({ characterName, metrics, loadingMetrics }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [showFadeTop, setShowFadeTop] = useState(false)
  const [showFadeBottom, setShowFadeBottom] = useState(false)

  const checkScroll = useCallback(() => {
    const el = scrollRef.current
    if (!el) return
    const atTop = el.scrollTop <= 0
    const atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 1
    const scrollable = el.scrollHeight > el.clientHeight
    setShowFadeTop(!atTop && scrollable)
    setShowFadeBottom(!atBottom && scrollable)
  }, [])

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    el.addEventListener('scroll', checkScroll, { passive: true })
    const observer = new ResizeObserver(checkScroll)
    observer.observe(el)
    checkScroll()
    return () => {
      el.removeEventListener('scroll', checkScroll)
      observer.disconnect()
    }
  }, [checkScroll])

  return (
    <div className="flex-1 min-w-0 relative">
      {showFadeTop && (
        <div className="absolute top-0 left-0 right-0 h-16 pointer-events-none" style={{ background: 'linear-gradient(to bottom, var(--rs-scroll-fade), transparent)' }} />
      )}
      <div ref={scrollRef} className="overflow-y-auto h-full">
        <div className="space-y-4">
          <CharacterHeader characterName={characterName} />

          <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
            <div className="xl:col-span-3">
              <MetricsCard metrics={metrics} />
            </div>
            <div className="xl:col-span-2">
              <QuestsCard metrics={metrics} />
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-6 gap-4">
            <div className="xl:col-span-2">
              <ActivityCard metrics={metrics} />
            </div>
            <div className="xl:col-span-4">
              <SkillsCard metrics={metrics} />
            </div>
          </div>
        </div>
      </div>
      {showFadeBottom && (
        <div className="absolute bottom-0 left-0 right-0 h-16 pointer-events-none" style={{ background: 'linear-gradient(to top, var(--rs-scroll-fade), transparent)' }} />
      )}
      <LoadingOverlay visible={loadingMetrics} fullScreen={false} />
    </div>
  )
}
