import { useMemo, type ReactNode } from 'react'
import { useCanvasParticles, type Particle, type ParticleConfig, type MaskSample } from '../particles'

const PARTICLE_COUNT = 20

function initParticle(p: Particle, w: number, h: number, randomizeLife: boolean, sampleMask?: () => MaskSample | null) {
  const pos = sampleMask?.()
  if (pos) {
    p.x = pos.x * w
    p.y = pos.y * h
  } else {
    p.x = Math.random() * w
    p.y = h * 0.3 + Math.random() * h * 0.5
  }
  p.vx = (Math.random() - 0.5) * 0.15
  p.vy = -(Math.random() * 0.2 + 0.03)
  p.size = Math.random() * 1.5 + 0.3
  p.maxLife = Math.random() * 200 + 80
  p.hue = Math.random() > 0.5 ? 1 : 0
  p.life = randomizeLife ? Math.random() * p.maxLife : 0
}

function drawParticle(ctx: CanvasRenderingContext2D, p: Particle, alpha: number) {
  const isBlue = p.hue === 1

  if (isBlue) {
    ctx.globalAlpha = alpha * 0.06
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 5, 0, Math.PI * 2)
    ctx.fillStyle = 'rgb(60, 180, 220)'
    ctx.fill()

    ctx.globalAlpha = alpha * 0.3
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 2, 0, Math.PI * 2)
    ctx.fillStyle = 'rgb(80, 200, 240)'
    ctx.fill()

    ctx.globalAlpha = alpha * 0.8
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 0.7, 0, Math.PI * 2)
    ctx.fillStyle = 'rgb(160, 240, 255)'
    ctx.fill()
  } else {
    ctx.globalAlpha = alpha * 0.04
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 4, 0, Math.PI * 2)
    ctx.fillStyle = 'rgb(200, 180, 120)'
    ctx.fill()

    ctx.globalAlpha = alpha * 0.25
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 1.5, 0, Math.PI * 2)
    ctx.fillStyle = 'rgb(220, 200, 140)'
    ctx.fill()

    ctx.globalAlpha = alpha * 0.6
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 0.6, 0, Math.PI * 2)
    ctx.fillStyle = 'rgb(240, 220, 170)'
    ctx.fill()
  }
}

export default function AmberfellBackground({ children }: { children: ReactNode }) {
  const config: ParticleConfig = useMemo(() => ({
    count: PARTICLE_COUNT,
    init: initParticle,
    draw: drawParticle,
    maskUrl: '/amberfell-wallpaper-mask.jpg',
  }), [])

  const canvasRef = useCanvasParticles(config)

  return (
    <div className="fixed inset-0 z-[-1]">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: 'url(/amberfell-wallpaper.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center 40%',
          backgroundRepeat: 'no-repeat',
        }}
      />
      <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(ellipse at center, transparent 15%, rgba(30, 20, 10, 0.6) 100%)' }} />
      <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" style={{ willChange: 'transform' }} />
      <div className="relative z-10">{children}</div>
    </div>
  )
}
