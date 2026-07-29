interface Props {
  visible: boolean
  fullScreen?: boolean
}

export default function LoadingOverlay({ visible, fullScreen = true }: Props) {
  if (!visible) return null

  return (
    <div
      role="status"
      aria-label="Loading"
      className={`${fullScreen ? 'fixed inset-0 bg-black/70 z-50' : 'absolute inset-0 bg-black/40 z-10 rounded-lg'} flex items-center justify-center pointer-events-none`}
    >
      <div className={`${fullScreen ? 'w-10 h-10' : 'w-8 h-8'} border-[3px] border-t-transparent rounded-full animate-spin`} style={{ borderColor: 'var(--rs-spinner)', borderTopColor: 'transparent' }} />
    </div>
  )
}
