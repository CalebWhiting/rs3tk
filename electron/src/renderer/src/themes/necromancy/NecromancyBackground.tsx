import { useMemo, type ReactNode } from 'react'
import { useCanvasParticles, type Particle, type ParticleConfig } from '../particles'
import BackgroundLayout from '../BackgroundLayout'

const ORB_COUNT = 20

function initOrb(p: Particle, w: number, h: number, randomizeLife: boolean) {
  p.x = Math.random() * w
  p.y = h * 0.3 + Math.random() * h * 0.5
  p.vx = (Math.random() - 0.5) * 0.3
  p.vy = -(Math.random() * 0.4 + 0.1)
  p.size = Math.random() * 2 + 0.5
  p.maxLife = Math.random() * 200 + 80
  p.life = randomizeLife ? Math.random() * p.maxLife : 0
}

function drawOrb(ctx: CanvasRenderingContext2D, p: Particle, alpha: number) {
  const heat = 1 - p.life / p.maxLife

  ctx.globalAlpha = alpha * 0.1
  ctx.beginPath()
  ctx.arc(p.x, p.y, p.size * 6, 0, Math.PI * 2)
  ctx.fillStyle = 'rgba(0, 220, 220, 1)'
  ctx.fill()

  ctx.globalAlpha = alpha * 0.4
  ctx.beginPath()
  ctx.arc(p.x, p.y, p.size * 2.5, 0, Math.PI * 2)
  ctx.fillStyle = 'rgba(100, 255, 255, 1)'
  ctx.fill()

  ctx.globalAlpha = alpha * 0.9
  ctx.beginPath()
  ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
  ctx.fillStyle = `rgba(200, 255, 255, ${heat})`
  ctx.fill()
}

const GLOW_STYLE: React.CSSProperties = {
  position: 'absolute',
  inset: 0,
  pointerEvents: 'none',
  background: 'radial-gradient(ellipse at 70% 20%, rgba(0,200,200,0.12) 0%, rgba(0,120,140,0.04) 40%, transparent 70%)',
}

export default function NecromancyBackground({ children }: { children: ReactNode }) {
  const config: ParticleConfig = useMemo(() => ({
    count: ORB_COUNT,
    init: initOrb,
    draw: drawOrb,
  }), [])

  const canvasRef = useCanvasParticles(config)

  return (
    <BackgroundLayout
      wallpaper="necromancy-wallpaper.png"
      vignette="radial-gradient(ellipse at center, transparent 30%, rgba(5, 15, 20, 0.7) 100%)"
      canvasRef={canvasRef}
    >
      <div style={GLOW_STYLE} />
      {children}
    </BackgroundLayout>
  )
}
