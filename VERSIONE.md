# RELEASE STATUS

Last updated: February 24, 2026

## Current version

- `3.4.0` (Stable)

Aligned files:
- `src/version.py`
- `pyproject.toml`
- `setup.py`

## Executed release gates

1. Full quality suite:
- Command: `python scripts/run_quality_suite.py`
- Result: **PASS**
- Outcome: `73 passed`, total coverage `84%`

2. Runtime smoke from source:
- Command: `AIRINGDECK_AUTO_EXIT_MS=12000 python src/main.py`
- Result: **PASS**

3. Build Windows:
- Command: `python scripts/build_windows.py`
- Result: **PASS**
- Output: `dist/AiringDeck.exe`

4. Runtime smoke on packaged build:
- Start `dist/AiringDeck.exe` with auto-exit
- Result: **PASS**

5. Build installer Windows:
- Command: `python scripts/build_windows_installer.py --skip-build-exe`
- Result: **PASS**
- Output: `dist/AiringDeck-Setup-3.4.0.exe`

## Key changes included in this release

- Settings menu redesigned with horizontal layout.
- Background periodic sync removed from settings.
- Added on-demand update check (`Controlla ora`) in settings.
- In-app updater flow now downloads and launches installer directly.

## Release-ready artifacts

- `dist/AiringDeck.exe`
- `dist/AiringDeck-Setup-3.4.0.exe`

## Recommended next cycle

- `3.4.1` patch (hardening in-app updater edge cases and installer lifecycle tests).
