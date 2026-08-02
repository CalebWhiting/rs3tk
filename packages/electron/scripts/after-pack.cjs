// electron-builder afterPack hook: disable Chromium sandboxing in packaged builds.
//
// `app.commandLine.appendSwitch('no-sandbox')` runs too late — Chromium's
// sandbox init happens in native code before the main-process JS loads.
// We fix this by replacing the Electron binary with a tiny shell wrapper
// that passes --no-sandbox to the real binary, so the flag is present in
// process.argv from the very start.
const fs = require('fs')
const path = require('path')

module.exports = async function (context) {
  const outDir = context.appOutDir

  // 1. Remove chrome-sandbox SUID helper
  const sandbox = path.join(outDir, 'chrome-sandbox')
  if (fs.existsSync(sandbox)) {
    fs.unlinkSync(sandbox)
  }

  // 2. Find the actual Electron binary — electron-builder lowercases the
  //    productName for Linux, but appInfo.productFilename preserves the
  //    original casing.  Also try with the -electron suffix since
  //    electron-builder appends that for the DEB/AppImage targets.
  const nameLC = context.packager.appInfo.productFilename.toLowerCase()
  const candidates = [
    path.join(outDir, nameLC),
    path.join(outDir, context.packager.appInfo.productFilename),
    path.join(outDir, `${nameLC}-electron`),
    path.join(outDir, `${context.packager.appInfo.productFilename}-electron`),
  ]

  const binary = candidates.find((p) => fs.existsSync(p))
  if (!binary) return

  const realBinary = `${binary}-bin`
  if (fs.existsSync(realBinary)) return

  fs.renameSync(binary, realBinary)

  // Use a relative path so the wrapper works inside the AppImage mount
  const relBin = path.basename(realBinary)
  fs.writeFileSync(
    binary,
    `#!/bin/sh\ncd "$(dirname "$0")"\nexec "./${relBin}" --no-sandbox "$@"\n`,
    { mode: 0o755 }
  )
}
