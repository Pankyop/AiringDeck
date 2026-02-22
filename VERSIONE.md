# RELEASE STATUS

Last updated: February 22, 2026

## Current version

- `3.3.0` (Stable)

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
- Output: `dist/AiringDeck-Setup-3.3.0.exe`

## Key changes included in this release

- Quality and release process consolidation (CI + changelog + release process).
- Complete removal of external rating-source feature, reverted to AniList-only scores.
- Simplified score UI (no provider label).
- Cleanup of model roles and code paths related to external rating providers.

## Release-ready artifacts

- `dist/AiringDeck.exe`
- `dist/AiringDeck-Setup-3.3.0.exe`

## Recommended next cycle

- `3.3.1` patch (post-release hardening and increased test coverage on `app_controller.py` branches).
