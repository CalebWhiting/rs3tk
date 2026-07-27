import { useMemo, type ReactNode } from 'react'
import { useCanvasParticles, type Particle, type ParticleConfig } from '../particles'
import BackgroundLayout from '../BackgroundLayout'

const WISP_COUNT = 22

function initWisp(p: Particle, w: number, h: number, randomizeLife: boolean) {
  p.x = Math.random() * w
  p.y = h * 0.35 + Math.random() * h * 0.55
  p.vx = (Math.random() - 0.5) * 0.25
  p.vy = -(Math.random() * 0.35 + 0.08)
  p.size = Math.random() * 2.2 + 0.4
  p.maxLife = Math.random() * 220 + 90
  p.hue = Math.random()
  p.life = randomizeLife ? Math.random() * p.maxLife : 0
}

function drawWisp(ctx: CanvasRenderingContext2D, p: Particle, alpha: number) {
  const heat = 1 - p.life / p.maxLife
  const isSoul = p.hue > 0.6

  if (isSoul) {
    ctx.globalAlpha = alpha * 0.08
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 7, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(180, 60, 200, 1)'
    ctx.fill()

    ctx.globalAlpha = alpha * 0.3
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(220, 80, 240, 1)'
    ctx.fill()

    ctx.globalAlpha = alpha * 0.8
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(255, 160, 255, ${heat})`
    ctx.fill()
  } else {
    ctx.globalAlpha = alpha * 0.07
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 6, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(0, 180, 200, 1)'
    ctx.fill()

    ctx.globalAlpha = alpha * 0.35
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 2.5, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(60, 220, 240, 1)'
    ctx.fill()

    ctx.globalAlpha = alpha * 0.85
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(180, 255, 255, ${heat})`
    ctx.fill()
  }
}

const GLOW_STYLE: React.CSSProperties = {
  position: 'absolute',
  inset: 0,
  pointerEvents: 'none',
  background: 'radial-gradient(ellipse at 40% 38%, rgba(160,80,200,0.10) 0%, rgba(0,160,180,0.06) 30%, transparent 60%)',
}

export default function SoulWarsBackground({ children }: { children: ReactNode }) {
  const config: ParticleConfig = useMemo(() => ({
    count: WISP_COUNT,
    init: initWisp,
    draw: drawWisp,
  }), [])

  const canvasRef = useCanvasParticles(config)

  return (
    <BackgroundLayout
      wallpaper="soul-wars-wallpaper.png"
      vignette="radial-gradient(ellipse at center, transparent 25%, rgba(5, 8, 18, 0.75) 100%)"
      canvasRef={canvasRef}
    >
      <div style={GLOW_STYLE} />
      {children}
    </BackgroundLayout>
  )
}
