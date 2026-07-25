import { useMemo, type ReactNode } from 'react'
import { useCanvasParticles, type Particle, type ParticleConfig } from '../particles'

const EMBER_COUNT = 15

function initEmber(p: Particle, w: number, h: number, randomizeLife: boolean) {
  const side = Math.random() > 0.5
  p.x = side ? 0.03 + Math.random() * 0.08 : 0.89 + Math.random() * 0.08
  p.y = 0.6 + Math.random() * 0.4
  p.vx = (Math.random() - 0.5) * 0.2
  p.vy = -(Math.random() * 0.3 + 0.08)
  p.size = Math.random() * 1.2 + 0.3
  p.maxLife = Math.random() * 150 + 60
  p.life = randomizeLife ? Math.random() * p.maxLife : 0
}

function drawEmber(ctx: CanvasRenderingContext2D, p: Particle, alpha: number) {
  const heat = 1 - p.life / p.maxLife
  const px = p.x * ctx.canvas.width / (window.devicePixelRatio || 1)
  const py = p.y * ctx.canvas.height / (window.devicePixelRatio || 1)
  const s = p.size

  ctx.globalAlpha = alpha * 0.15
  ctx.fillStyle = `rgb(255,${200 + (heat * 40) | 0},${80 + (heat * 60) | 0})`
  ctx.fillRect(px - s * 3, py - s * 3, s * 6, s * 6)

  ctx.globalAlpha = alpha * 0.6
  ctx.fillStyle = `rgb(255,${220 + (heat * 30) | 0},${120 + (heat * 50) | 0})`
  ctx.fillRect(px - s, py - s, s * 2, s * 2)
}

export default function RaptorBackground({ children }: { children: ReactNode }) {
  const config: ParticleConfig = useMemo(() => ({
    count: EMBER_COUNT,
    init: initEmber,
    draw: drawEmber,
  }), [])

  const canvasRef = useCanvasParticles(config)

  return (
    <div className="fixed inset-0 z-[-1]">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: 'url(/raptor-wallpaper.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: '75% center',
          backgroundRepeat: 'no-repeat',
        }}
      />
      <div className="absolute inset-0 raptor-vignette pointer-events-none" />
      <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" style={{ willChange: 'transform' }} />
      <div className="relative z-10 raptor-content-backdrop">{children}</div>
    </div>
  )
}
