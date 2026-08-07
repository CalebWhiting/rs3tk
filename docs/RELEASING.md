# Releasing

## 1. Write the changelog

Add a `## vX.Y.Z` section to `CHANGELOG.md` following the existing format.
Each entry should be a bullet point with a **bold title** and a brief
description of the change. Commit the changelog before proceeding.

## 2. Run the release script

```bash
scripts/release.sh X.Y.Z
```

This single command:

1. Validates the version format (`MAJOR.MINOR.PATCH`)
2. Checks the git working tree is clean
3. Checks the tag does not already exist
4. Bumps the version across all 10 tracked locations (see below)
5. Regenerates lockfiles (`uv lock`, `pnpm install`)
6. Commits, tags, and pushes

## 3. What happens automatically

The tag push triggers `.github/workflows/release.yml`, which runs four
jobs:

| Job | What it does | Destination |
|-----|-------------|-------------|
| **pypi** | Builds and publishes `rs3tk-core` + `rs3tk` wheels/sdists | PyPI |
| **appimage** | Builds bridge (PyInstaller), Electron app, AppImage + .deb + .rpm | GitHub Releases |
| **copr** | Downloads the .rpm from the release and submits it | Fedora Copr |
| **aur** | Updates `rs3tk-bin` PKGBUILD with new AppImage checksum | AUR |

All four jobs run in parallel (copr and aur depend on appimage completing
first).

## 4. Troubleshooting

**A CI job failed:** Go to Actions > release workflow > re-run the failed
job. The release workflow can be re-run safely — PyPI uses
`skip-existing: true`, and GitHub Release uploads are idempotent.

**PyPI publish failed:** Check the [PyPI project
page](https://pypi.org/project/rs3tk/) — the version may have partially
published. If so, `skip-existing` will handle it on re-run.

**AUR push failed:** The AUR git repo may have a conflict. Clone
`aur.archlinux.org/rs3tk-bin.git`, resolve, and push manually.

**Copr build failed:** Check the [Copr build
page](https://copr.fedoraproject.org/coprs/calebwhiting/rs3tk/) for
build logs. You can re-submit manually with `copr-cli create-build`.

## Local packaging

To test package builds locally without publishing:

```bash
# Build DEB, RPM, APK, or Arch packages in Docker
bash scripts/package-linux.sh --deb
bash scripts/package-linux.sh --rpm
bash scripts/package-linux.sh --apk
bash scripts/package-linux.sh --arch

# Test the Electron AppImage in Docker
bash scripts/test-electron.sh
```
