import { useMemo, type ReactNode } from 'react'
import { useCanvasParticles, type Particle, type ParticleConfig } from '../particles'

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

function ambientGlow(ctx: CanvasRenderingContext2D, w: number, h: number, t: number) {
  const flicker = Math.sin(t * 0.03) * 0.02 + Math.sin(t * 0.08) * 0.01
  const ambGrad = ctx.createRadialGradient(w * 0.7, h * 0.2, 0, w * 0.7, h * 0.2, w * 0.6)
  ambGrad.addColorStop(0, `rgba(0, 200, 200, ${0.12 + flicker})`)
  ambGrad.addColorStop(0.4, `rgba(0, 120, 140, ${0.06 + flicker * 0.5})`)
  ambGrad.addColorStop(1, 'rgba(0, 40, 50, 0)')
  ctx.fillStyle = ambGrad
  ctx.fillRect(0, 0, w, h)
}

export default function NecromancyBackground({ children }: { children: ReactNode }) {
  const config: ParticleConfig = useMemo(() => ({
    count: ORB_COUNT,
    init: initOrb,
    draw: drawOrb,
    ambient: ambientGlow,
  }), [])

  const canvasRef = useCanvasParticles(config)

  return (
    <div className="fixed inset-0 z-[-1]">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: 'url(/necromancy-wallpaper.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
        }}
      />
      <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(ellipse at center, transparent 30%, rgba(5, 15, 20, 0.7) 100%)' }} />
      <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" style={{ willChange: 'transform' }} />
      <div className="relative z-10">{children}</div>
    </div>
  )
}
