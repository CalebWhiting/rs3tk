# TODO

## CI/CD Pipeline

**Priority:** Medium  
**Status:** Not started

The repo is on Codeberg (Forgejo-based). Use Forgejo Actions via `.forgejo/workflows/`.

### Distribution Strategy

Two artifacts, one install flow:

| Artifact | Distribution | Size | User action |
|----------|-------------|------|-------------|
| Python package | PyPI (`pip install rs3tk`) | ~50KB | `pip install rs3tk` |
| Electron GUI | Codeberg Releases (AppImage) | ~110MB | Download & run |

### Workflows to Create

1. **Lint + Test** (on every push / PR)
   - `ruff check src/ tests/`
   - `ruff format --check src/ tests/`
   - `mypy src/`
   - `pytest --cov=rs3tk`

2. **Python Package Publish** (on tag push `v*`)
   - Build sdist + wheel
   - Publish to PyPI
   - Entry points: `rs3tk` (CLI), `rs3tk-backend` (backend server)

3. **Electron AppImage Build** (on tag push `v*`)
   - `npm run build:linux` → AppImage
   - Upload to Codeberg Releases as `RS3TK-{version}.AppImage`

4. **Release Automation**
   - Single tag push triggers both builds
   - Auto-generate release notes from commits
   - Attach AppImage + checksums to release

### Future Considerations

- AUR package for Arch Linux users
- Install script (`curl | bash`) for one-command setup
- Version mismatch warning in Electron when CLI/backend version differs
