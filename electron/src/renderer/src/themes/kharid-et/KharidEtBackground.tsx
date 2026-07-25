import { useMemo, type ReactNode } from 'react'
import { useCanvasParticles, type Particle, type ParticleConfig } from '../particles'

const WISP_COUNT = 18

function initWisp(p: Particle, w: number, h: number, randomizeLife: boolean) {
  p.x = Math.random() * w
  p.y = h * 0.4 + Math.random() * h * 0.5
  p.vx = (Math.random() - 0.5) * 0.2
  p.vy = -(Math.random() * 0.3 + 0.05)
  p.size = Math.random() * 2 + 0.5
  p.maxLife = Math.random() * 180 + 60
  p.hue = Math.random() > 0.6 ? 280 : 40
  p.life = randomizeLife ? Math.random() * p.maxLife : 0
}

function drawWisp(ctx: CanvasRenderingContext2D, p: Particle, alpha: number) {
  const isPurple = p.hue === 280

  ctx.globalAlpha = alpha * 0.08
  ctx.beginPath()
  ctx.arc(p.x, p.y, p.size * 5, 0, Math.PI * 2)
  ctx.fillStyle = isPurple ? 'rgb(180, 80, 220)' : 'rgb(220, 180, 80)'
  ctx.fill()

  ctx.globalAlpha = alpha * 0.35
  ctx.beginPath()
  ctx.arc(p.x, p.y, p.size * 2, 0, Math.PI * 2)
  ctx.fillStyle = isPurple ? 'rgb(200, 120, 255)' : 'rgb(240, 200, 100)'
  ctx.fill()

  ctx.globalAlpha = alpha * 0.8
  ctx.beginPath()
  ctx.arc(p.x, p.y, p.size * 0.8, 0, Math.PI * 2)
  ctx.fillStyle = isPurple ? 'rgb(230, 180, 255)' : 'rgb(255, 230, 150)'
  ctx.fill()
}

export default function KharidEtBackground({ children }: { children: ReactNode }) {
  const config: ParticleConfig = useMemo(() => ({
    count: WISP_COUNT,
    init: initWisp,
    draw: drawWisp,
  }), [])

  const canvasRef = useCanvasParticles(config)

  return (
    <div className="fixed inset-0 z-[-1]">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: 'url(/kharid-et-wallpaper.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center 30%',
          backgroundRepeat: 'no-repeat',
        }}
      />
      <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(ellipse at center, transparent 20%, rgba(20, 10, 30, 0.65) 100%)' }} />
      <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" style={{ willChange: 'transform' }} />
      <div className="relative z-10">{children}</div>
    </div>
  )
}
