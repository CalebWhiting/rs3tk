import { useState, useEffect, useRef } from 'react'

interface Props {
  characterName: string | null
}

function avatarCdnUrl(name: string | null): string {
  if (!name) return '/avatar_default.png'
  return `https://secure.runescape.com/m=avatar-rs/${encodeURIComponent(name)}/chat.png`
}

export default function CharacterHeader({ characterName }: Props) {
  const measureRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [showAvatar, setShowAvatar] = useState(true)
  const [avatarUrl, setAvatarUrl] = useState('/avatar_default.png')

  useEffect(() => {
    setAvatarUrl(avatarCdnUrl(characterName))
  }, [characterName])

  useEffect(() => {
    const measure = measureRef.current
    const container = containerRef.current
    if (!measure || !container) return

    const check = () => {
      const containerWidth = container.getBoundingClientRect().width
      const avatarSpace = 80 + 16
      const starWidth = 32
      const gaps = 4 * 8
      const available = containerWidth - avatarSpace - starWidth - gaps
      const textWidth = measure.getBoundingClientRect().width
      setShowAvatar(textWidth <= available)
    }

    const observer = new ResizeObserver(check)
    observer.observe(container)
    check()
    return () => observer.disconnect()
  }, [characterName])

  return (
    <>
      <div ref={measureRef} className="fixed top-0 left-0 invisible pointer-events-none text-2xl font-bold whitespace-nowrap">
        {characterName || 'Not logged in'}
      </div>
      <div ref={containerRef} className="flex items-center gap-4 mb-4">
        {showAvatar && (
          <div className="w-20 h-20 rounded-full border-2 border-rs-gold bg-rs-card flex items-center justify-center overflow-hidden flex-shrink-0">
            <img src={avatarUrl} alt="Avatar" className="w-[76px] h-[76px] rounded-full" onError={(e) => { e.currentTarget.src = '/avatar_default.png' }} />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 min-w-0">
            <h1 className="text-2xl font-bold truncate min-w-0 flex-1">
              {characterName || 'Not logged in'}
            </h1>
            <span className="text-rs-gold text-lg flex-shrink-0 member-symbol"></span>
          </div>
        </div>
      </div>
    </>
  )
}
