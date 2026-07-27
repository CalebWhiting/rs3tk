# TODO

## GitHub Actions CI/CD Pipeline

**Priority:** Medium  
**Status:** Not started

### Distribution Strategy

Two artifacts, one install flow:

| Artifact | Distribution | Size | User action |
|----------|-------------|------|-------------|
| Python package | PyPI (`pip install rs3tk`) | ~50KB | `pip install rs3tk` |
| Electron GUI | GitHub Releases (AppImage) | ~110MB | Download & run |

### Workflows to Create

1. **Python Package Publish**
   - Build sdist + wheel on tag push (`v*`)
   - Publish to PyPI via `pypa/gh-action-pypi-publish`
   - Entry points: `rs3tk` (CLI), `rs3tk-backend` (backend server)

2. **Electron AppImage Build**
   - Build on tag push (`v*`) or manual dispatch
   - `npm run build:linux` → AppImage
   - Upload to GitHub Releases as `RS3TK-{version}.AppImage`

3. **Release Automation**
   - Single tag push triggers both builds
   - Auto-generate release notes from commits
   - Attach AppImage + checksums to release

### Future Considerations

- AUR package for Arch Linux users
- Install script (`curl | bash`) for one-command setup
- Version mismatch warning in Electron when CLI/backend version differs
