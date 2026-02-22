# AiringDeck - Implementation Roadmap

Last updated: February 22, 2026

## 1) Current status

- Current version: `3.3.0` (stable).
- Windows build: OK (`scripts/build_windows.py`, output: `dist/AiringDeck.exe`).
- Windows installer: OK (`scripts/build_windows_installer.py`, output: `dist/AiringDeck-Setup-3.3.0.exe`).
- Quality suite: OK (`73 passed`).
- Total coverage: `84%`.
- Security scan (`bandit`) and dependency policy sync: OK.
- Runtime smoke (source + dist): OK.

Conclusion: stable release completed and publishable.

## 2) Completed for release 3.3.0

- Core/service hardening (error handling and logging consistency).
- Minimal CI enabled (lint + security + tests + build smoke).
- Changelog and release process formalized.
- Keyboard/focus accessibility improved across key UI components.
- Critical UI layout fixes (long titles, toolbar, details panel).
- Removed multi-provider rating stack and returned to AniList-only scores for stability.

## 3) Post-release backlog (3.3.x)

### P1 - High priority (next cycle)

- Expand coverage for remaining UI/network edge cases.
- Improve coverage in less-exercised `app_controller.py` branches.
- Add automated tests for update flow (accept/dismiss/open link).
- Reduce non-blocking PyInstaller warnings (`pycparser.lextab/yacctab`).

### P2 - Functional evolution

- Configurable background sync (intervals + adaptive backoff).
- Migrate local storage from QSettings to SQLite (versioned schema).
- Improve installer test coverage (install/upgrade/uninstall).

### P3 - Process and release management

- Automate release notes from changelog/tag.
- Expand CI matrix (more Windows/Python environments).
- Enforce release branch policy with mandatory CI gates.

## 4) Suggested version roadmap

- `3.3.1` (patch): post-release fixes and additional test/CI hardening.
- `3.4.0` (minor): background sync + first storage improvements.
- `3.4.1+` (patch): stabilization of the 3.4 line.

## 5) Definition of Done for next releases

- CI green.
- Coverage >= 80%.
- No naked `except:` in core/services.
- Changelog updated.
- Release tag created.
- `dist` build and installer generated without errors.
