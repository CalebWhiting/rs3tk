export function formatXp(xp: number): string {
  if (xp < 10_000) return xp.toLocaleString()
  if (xp < 1_000_000) {
    const major = Math.floor(xp / 1_000)
    const minor = Math.floor((xp % 1_000) / 100)
    return minor ? `${major}.${minor}K` : `${major}K`
  }
  if (xp < 1_000_000_000) {
    const major = Math.floor(xp / 1_000_000)
    const minor = Math.floor((xp % 1_000_000) / 10_000)
    return minor ? `${major}.${minor.toString().padStart(2, '0')}M` : `${major}M`
  }
  const major = Math.floor(xp / 1_000_000_000)
  const minor = Math.floor((xp % 1_000_000_000) / 10_000_000)
  return minor ? `${major}.${minor.toString().padStart(2, '0')}B` : `${major}B`
}

export function formatXpScaled(xp: number): string {
  return formatXp(xp / 10)
}
