// electron-builder afterPack hook: fix chrome-sandbox ownership and permissions.
// The build must run under `fakeroot` so that chown to root:root is faked and
// recorded correctly in the squashfs image that electron-builder creates.
const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

module.exports = async function (context) {
  const sandbox = path.join(context.appOutDir, 'chrome-sandbox')
  if (!fs.existsSync(sandbox)) return

  try {
    execSync(`chown root:root "${sandbox}"`, { stdio: 'inherit' })
    execSync(`chmod 4755 "${sandbox}"`, { stdio: 'inherit' })
  } catch {
    // If the chown fails (e.g. not running under fakeroot), remove the binary
    // so the AppImage at least launches without sandboxing.
    fs.unlinkSync(sandbox)
  }
}
