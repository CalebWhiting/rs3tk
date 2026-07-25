"""Refactor strategy for standalone installer scripts.

These script files must remain self-contained and independently runnable.
"""

## Current State

All 4 installer scripts (`rs3.py`, `osclient.py`, `hdos.py`, `runelite.py`) are standalone Python scripts that:
1. Can be run directly: `python script.py --install-only`
2. Can be found in PATH and executed
3. Don't import from rs3tk or each other

## Refactoring Challenges

These scripts need to stay standalone because:
- **Self-Modification**: Installing updates requires replacing the executable file
- **No External Dependencies**: Can't rely on rs3tk being installed
- **Update Isolation**: Each script updates and replaces only its own binary
- **User Management**: Users can run scripts manually without rs3tk

## Recommended Simplification Approach

Instead of extracting common logic into base classes, here's what's most effective:

### 1. Extract utilities to top-level functions
Create common utility functions that don't require imports:

```python
# In a shared utils.py that both install.py and scripts can use
def progress(text): ...
def end_progress(): ...
def is_exec(path): ...
```

But this still creates a dependency.

### 2. Better: Extract to shared config file
Each script can import constants and simple helpers from:
- File-based configuration
- shell environment variables
- System paths

### 3. Clean up existing duplicate progress tracking
Each script has identical `_progress()` function:
- `hdos.py:21-27`
- `osclient.py:23-27`  
- `runelite.py:23-29`
- `rs3.py:22-40`

**Solution**: Share progress tracking via shell redirection or simple print statements that work independently.

### 4. For installer.py (the Python installer framework)
This actually CAN be refactored since:
- It's part of rs3tk
- Not distributed to users
- Contains ClientInstaller base class that can have common logic

## Practical Refactoring Steps

1. **Simplify `install.py`**:
   - Extract `_write_script()` to `_download_utils.py`
   - Move progress tracking to `_progress.py`
   - Keep ClientInstaller ABC clean

2. **Remove duplicate progress functions** from data/ directory:
   - Keep simple `print()` based progress in scripts
   - No shared utilities needed

3. **Standardize error handling** in install.py:
   - Consolidate error types
   - Better error messages

4. **Simplify installer classes**:
   - Remove docstrings from install() methods
   - Use ... ellipsis for abstract methods
   - Clean up type hints

## Benefits of This Approach

- **Maintains standalone**: Scripts remain runnable as-is
- **Reduces code duplication**: Common installer framework simplified
- **Improves maintainability**: Central error handling and progress tracking
- **No breaking changes**: Scripts still work exactly the same way
- **Better separation**: Core installer logic centralized, distributed scripts kept simple

## Files to Modify

- `src/rs3tk/install.py`: Refactor ABC, extract utils
- `src/rs3tk/data/*.py`: Remove duplicate progress functions
- **NOT modified**: installer scripts themselves

This preserves the intentional architecture while cleaning up unnecessary duplication.
