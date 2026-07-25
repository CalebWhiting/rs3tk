# Refactor plan

## 1. Remove common boilerplate in CLI commands
- Remove redundant AppError error wrapping in CLI

## 2. Consolidate error handling
- Extract error handling into a decorator or helper
- Standardize error message formatting

## 3. Deduplicate imports
- Move imported modules to top of cli.py
- Remove per-command imports

## 4. Break down large functions in app.py
- Extract auth/login helper functions
- Simplify _fetch_all() nested function
- Separate concerns in launch_game()

## 5. Standardize HTTP client usage
- Make game.py use async httpx like the rest
- Update all callers to use async

## 6. Refactor installer framework
- Create base ClientInstaller in install.py
- Move common progress tracking to utils
- Add common factory pattern

## 7. Simplify auth/session.py
- Extract constants
- Simplify login flow
- Consolidate session creation logic

## 8. Simplify jagex_api.py
- Extract session management
- Reduce complexity of create_session()
- Improve error handling

## 9. Extract API client common logic
- Create base HTTP client class
- Move common response handling
- Standardize API error handling

## 10. Create comprehensive test suite
- Add tests for all CLI commands
- Add tests for auth flow
- Add tests for API calls
- Add tests for installer logic

## 11. Clean up file structure
- Remove unused files
- Fix package.json (if exists)
- Remove Electron src/gui/ directory
- Add __pycache__ exclusion