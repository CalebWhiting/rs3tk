// electron-builder afterPack hook: remove chrome-sandbox from packaged output.
// The SUID sandbox helper needs root:root 4755 permissions AND unrestricted
// user namespaces.  VMs / containers typically restrict user namespaces, so
// even a correctly-permissioned binary fails with "Operation not permitted".
// Removing the binary makes Chromium fall back to non-sandboxed mode.
const fs = require('fs')
const path = require('path')

module.exports = async function (context) {
  const sandbox = path.join(context.appOutDir, 'chrome-sandbox')
  if (fs.existsSync(sandbox)) {
    fs.unlinkSync(sandbox)
  }
}
