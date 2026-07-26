import { type ReactNode, type Ref, type CSSProperties } from 'react'

interface Props {
  wallpaper: string
  wallpaperPosition?: string
  vignette?: string
  vignetteStyle?: CSSProperties
  vignetteClassName?: string
  canvasRef: Ref<HTMLCanvasElement>
  children: ReactNode
  contentClassName?: string
}

const DEFAULT_VIGNETTE = 'radial-gradient(ellipse at center, transparent 25%, rgba(5, 10, 20, 0.7) 100%)'

export default function BackgroundLayout({
  wallpaper,
  wallpaperPosition = 'center',
  vignette = DEFAULT_VIGNETTE,
  vignetteStyle,
  vignetteClassName = '',
  canvasRef,
  children,
  contentClassName = '',
}: Props) {
  return (
    <div className="fixed inset-0 z-[-1]">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `url(${wallpaper})`,
          backgroundSize: 'cover',
          backgroundPosition: wallpaperPosition,
          backgroundRepeat: 'no-repeat',
        }}
      />
      <div
        className={`absolute inset-0 pointer-events-none ${vignetteClassName}`}
        style={vignetteStyle ?? (vignetteClassName ? undefined : { background: vignette })}
      />
      <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" style={{ willChange: 'transform' }} />
      <div className={`relative z-10 ${contentClassName}`}>{children}</div>
    </div>
  )
}
