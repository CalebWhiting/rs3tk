// electron-builder afterPack hook: remove chrome-sandbox from packaged output.
// The SUID sandbox helper requires root:root 4755 permissions which most
// end-user systems won't have.  Without the binary Chromium simply falls back
// to non-sandboxed mode, which is fine for a desktop game launcher.
const fs = require('fs')
const path = require('path')

module.exports = async function (context) {
  const sandbox = path.join(context.appOutDir, 'chrome-sandbox')
  if (fs.existsSync(sandbox)) {
    fs.unlinkSync(sandbox)
  }
}
