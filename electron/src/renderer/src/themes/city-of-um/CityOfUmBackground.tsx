import { useMemo, type ReactNode } from 'react'
import { useCanvasParticles, type Particle, type ParticleConfig } from '../particles'

const WISP_COUNT = 18

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

function ambientGlow(ctx: CanvasRenderingContext2D, w: number, h: number, t: number) {
  const flicker = Math.sin(t * 0.025) * 0.015 + Math.sin(t * 0.06) * 0.008
  const ambGrad = ctx.createRadialGradient(w * 0.35, h * 0.45, 0, w * 0.35, h * 0.45, w * 0.6)
  ambGrad.addColorStop(0, `rgba(0, 180, 160, ${0.10 + flicker})`)
  ambGrad.addColorStop(0.5, `rgba(0, 100, 120, ${0.04 + flicker * 0.5})`)
  ambGrad.addColorStop(1, 'rgba(0, 40, 60, 0)')
  ctx.fillStyle = ambGrad
  ctx.fillRect(0, 0, w, h)

  const glowGrad = ctx.createRadialGradient(w * 0.4, h * 0.15, 0, w * 0.4, h * 0.15, w * 0.3)
  glowGrad.addColorStop(0, `rgba(80, 255, 160, ${0.04 + flicker * 0.3})`)
  glowGrad.addColorStop(1, 'rgba(40, 200, 120, 0)')
  ctx.fillStyle = glowGrad
  ctx.fillRect(0, 0, w, h)
}

export default function CityOfUmBackground({ children }: { children: ReactNode }) {
  const config: ParticleConfig = useMemo(() => ({
    count: WISP_COUNT,
    init: initWisp,
    draw: drawWisp,
    ambient: ambientGlow,
  }), [])

  const canvasRef = useCanvasParticles(config)

  return (
    <div className="fixed inset-0 z-[-1]">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: 'url(/city-of-um-wallpaper.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
        }}
      />
      <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(ellipse at center, transparent 25%, rgba(5, 10, 20, 0.7) 100%)' }} />
      <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" style={{ willChange: 'transform' }} />
      <div className="relative z-10">{children}</div>
    </div>
  )
}
