import { useRef, useEffect, useState, useCallback } from 'react'

export interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  life: number
  maxLife: number
  [key: string]: number
}

export interface MaskSample {
  x: number
  y: number
}

export interface ParticleConfig {
  count: number
  init: (p: Particle, w: number, h: number, randomizeLife: boolean, sampleMask?: () => MaskSample | null) => void
  draw: (ctx: CanvasRenderingContext2D, p: Particle, alpha: number, t: number, i: number) => void
  ambient?: (ctx: CanvasRenderingContext2D, w: number, h: number, t: number) => void
  maskUrl?: string
}

export function particleAlpha(p: Particle, fadeInFrames = 20, fadeOutFrames = 30): number {
  const fadeIn = p.life < fadeInFrames ? p.life / fadeInFrames : 1
  const fadeOut = p.life > p.maxLife - fadeOutFrames ? (p.maxLife - p.life) / fadeOutFrames : 1
  return fadeIn * Math.max(0, fadeOut)
}

export function useDisableEffects(): boolean {
  const [disabled, setDisabled] = useState(() => {
    try { return localStorage.getItem('rs3tk-disable-effects') === 'true' } catch { return false }
  })
  useEffect(() => {
    const onEffectChange = (e: Event) => setDisabled((e as CustomEvent<boolean>).detail)
    window.addEventListener('rs3tk-disable-effects', onEffectChange)
    return () => window.removeEventListener('rs3tk-disable-effects', onEffectChange)
  }, [])
  return disabled
}

function loadMask(url: string): Promise<{ data: Uint8ClampedArray; w: number; h: number; brightPixels: { x: number; y: number }[] } | null> {
  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d')!
      ctx.drawImage(img, 0, 0)
      const imageData = ctx.getImageData(0, 0, img.width, img.height)
      const brightPixels: { x: number; y: number }[] = []
      for (let y = 0; y < img.height; y++) {
        for (let x = 0; x < img.width; x++) {
          const i = (y * img.width + x) * 4
          const brightness = imageData.data[i]
          if (brightness > 128) {
            brightPixels.push({ x, y })
          }
        }
      }
      resolve({ data: imageData.data, w: img.width, h: img.height, brightPixels })
    }
    img.onerror = () => resolve(null)
    img.src = url
  })
}

export function useCanvasParticles(config: ParticleConfig) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const particlesRef = useRef<Particle[]>([])
  const animRef = useRef<number>(0)
  const timeRef = useRef<number>(0)
  const maskRef = useRef<{ data: Uint8ClampedArray; w: number; h: number; brightPixels: { x: number; y: number }[] } | null>(null)
  const disabled = useDisableEffects()

  useEffect(() => {
    if (config.maskUrl) {
      loadMask(config.maskUrl).then((mask) => { maskRef.current = mask })
    }
  }, [config.maskUrl])

  const sampleMask = useCallback((): MaskSample | null => {
    const mask = maskRef.current
    if (!mask || mask.brightPixels.length === 0) return null
    const pixel = mask.brightPixels[Math.floor(Math.random() * mask.brightPixels.length)]
    return { x: pixel.x / mask.w, y: pixel.y / mask.h }
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    if (disabled) {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      return
    }

    const dpr = window.devicePixelRatio || 1
    let w = canvas.width
    let h = canvas.height
    const resize = () => {
      w = window.innerWidth
      h = window.innerHeight
      canvas.width = w * dpr
      canvas.height = h * dpr
      canvas.style.width = w + 'px'
      canvas.style.height = h + 'px'
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }
    resize()
    window.addEventListener('resize', resize)

    if (particlesRef.current.length === 0) {
      for (let i = 0; i < config.count; i++) {
        const p: Particle = { x: 0, y: 0, vx: 0, vy: 0, size: 0, life: 0, maxLife: 0 }
        config.init(p, w, h, true, sampleMask)
        particlesRef.current.push(p)
      }
    }

    const animate = () => {
      timeRef.current++
      const t = timeRef.current
      ctx.clearRect(0, 0, w, h)

      if (config.ambient) config.ambient(ctx, w, h, t)

      const particles = particlesRef.current
      for (let i = 0; i < config.count; i++) {
        const p = particles[i]
        p.life++
        p.x += p.vx + Math.sin(t * 0.015 + i * 1.2) * 0.15
        p.y += p.vy

        const alpha = particleAlpha(p)
        config.draw(ctx, p, alpha, t, i)

        if (p.life > p.maxLife || p.y < -10) {
          config.init(p, w, h, false, sampleMask)
        }
      }
      ctx.globalAlpha = 1

      animRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => { window.removeEventListener('resize', resize); cancelAnimationFrame(animRef.current) }
  }, [disabled, config, sampleMask])

  return canvasRef
}
