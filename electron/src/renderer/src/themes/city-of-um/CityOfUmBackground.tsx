import { useMemo, useState, useEffect, type ReactNode } from 'react'
import { useCanvasParticles, type Particle, type ParticleConfig } from '../particles'
import BackgroundLayout from '../BackgroundLayout'

const WISP_COUNT = 18

const IMAGE_W = 1920
const IMAGE_H = 1080
const LIGHTHOUSE_CX = 767
const LIGHTHOUSE_CY = 171.5

function imageToViewport(ix: number, iy: number, vw: number, vh: number): { x: number; y: number } {
  const imageAspect = IMAGE_W / IMAGE_H
  const viewportAspect = vw / vh

  if (viewportAspect > imageAspect) {
    const scale = vw / IMAGE_W
    const scaledH = IMAGE_H * scale
    const offsetY = (vh - scaledH) / 2
    return { x: ix * scale, y: iy * scale + offsetY }
  }
  const scale = vh / IMAGE_H
  const scaledW = IMAGE_W * scale
  const offsetX = (vw - scaledW) / 2
  return { x: ix * scale + offsetX, y: iy * scale }
}

function initWisp(p: Particle, w: number, h: number, randomizeLife: boolean) {
  p.x = Math.random() * w
  p.y = h * 0.4 + Math.random() * h * 0.5
  p.vx = (Math.random() - 0.5) * 0.3
  p.vy = -(Math.random() * 0.4 + 0.1)
  p.size = Math.random() * 2 + 0.5
  p.maxLife = Math.random() * 250 + 100
  p.hue = 160 + Math.random() * 30
  p.life = randomizeLife ? Math.random() * p.maxLife : 0
}

function drawWisp(ctx: CanvasRenderingContext2D, p: Particle, alpha: number) {
  ctx.globalAlpha = alpha * 0.08
  ctx.beginPath()
  ctx.arc(p.x, p.y, p.size * 8, 0, Math.PI * 2)
  ctx.fillStyle = `hsla(${p.hue}, 70%, 50%, 1)`
  ctx.fill()

  ctx.globalAlpha = alpha * 0.3
  ctx.beginPath()
  ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2)
  ctx.fillStyle = `hsla(${p.hue}, 80%, 65%, 1)`
  ctx.fill()

  ctx.globalAlpha = alpha * 0.8
  ctx.beginPath()
  ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
  ctx.fillStyle = `hsla(${p.hue}, 90%, 85%, 0.9)`
  ctx.fill()
}

export default function CityOfUmBackground({ children }: { children: ReactNode }) {
  const config: ParticleConfig = useMemo(() => ({
    count: WISP_COUNT,
    init: initWisp,
    draw: drawWisp,
  }), [])

  const canvasRef = useCanvasParticles(config)

  const [glowStyle, setGlowStyle] = useState<React.CSSProperties>({})

  useEffect(() => {
    const update = () => {
      const lh = imageToViewport(LIGHTHOUSE_CX, LIGHTHOUSE_CY, window.innerWidth, window.innerHeight)
      const pxPct = (lh.x / window.innerWidth) * 100
      const pyPct = (lh.y / window.innerHeight) * 100
      setGlowStyle({
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        background: [
          `radial-gradient(ellipse at ${pxPct}% ${pyPct}%, rgba(0,180,160,0.12) 0%, rgba(0,80,100,0.04) 40%, transparent 70%)`,
          `radial-gradient(ellipse at ${pxPct}% ${pyPct}%, rgba(80,255,160,0.04) 0%, transparent 30%)`,
          'rgba(0,64,80,0.08)',
        ].join(', '),
      })
    }
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [])

  return (
    <BackgroundLayout
      wallpaper="city-of-um-wallpaper.jpg"
      vignette=""
      canvasRef={canvasRef}
    >
      <div style={glowStyle} />
      {children}
    </BackgroundLayout>
  )
}
