import { useEffect, useRef } from 'react'
import { useTheme, useSlot } from '../lib/theme'

const noiseCache = new Map<string, string>()

function generateNoise(width: number, height: number, r: number, g: number, b: number): string {
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')!
  const imageData = ctx.createImageData(width, height)
  const data = imageData.data
  for (let i = 0; i < data.length; i += 4) {
    const n = Math.floor(Math.random() * 5) - 2
    data[i] = Math.max(0, Math.min(255, r + n))
    data[i + 1] = Math.max(0, Math.min(255, g + n))
    data[i + 2] = Math.max(0, Math.min(255, b + n))
    data[i + 3] = 255
  }
  ctx.putImageData(imageData, 0, 0)
  const url = canvas.toDataURL()
  return url
}

function getNoiseUrl(r: number, g: number, b: number): string {
  const key = `${r},${g},${b}`
  let url = noiseCache.get(key)
  if (!url) {
    url = generateNoise(256, 256, r, g, b)
    noiseCache.set(key, url)
  }
  return url
}

function DefaultBackground({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)
  const { theme } = useTheme()

  useEffect(() => {
    if (!ref.current) return
    const r = parseInt(theme.vars['--rs-noise-r'] || '14', 10)
    const g = parseInt(theme.vars['--rs-noise-g'] || '23', 10)
    const b = parseInt(theme.vars['--rs-noise-b'] || '29', 10)
    const noiseUrl = getNoiseUrl(r, g, b)
    ref.current.style.backgroundImage = `url(${noiseUrl})`
    ref.current.style.backgroundRepeat = 'repeat'
  }, [theme])

  return (
    <div ref={ref} className="fixed inset-0 z-[-1]">
      {children}
    </div>
  )
}

export default function NoiseBackground({ children }: { children: React.ReactNode }) {
  const { theme } = useTheme()
  const BackgroundSlot = useSlot('background')

  if (BackgroundSlot) {
    return <BackgroundSlot theme={theme}>{children}</BackgroundSlot>
  }

  return <DefaultBackground>{children}</DefaultBackground>
}
