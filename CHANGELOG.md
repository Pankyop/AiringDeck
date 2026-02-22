# Changelog

All notable changes to this project are documented in this file.

This project follows Keep a Changelog and Semantic Versioning.

## [Unreleased]

### Changed
- 

### Fixed
- 

### CI
- 

## [3.3.0] - 2026-02-22

### Changed
- Promoted the stable release from `3.3.0-beta.1` to `3.3.0`.
- Removed external score-source selection and switched back to AniList-only scores.
- Simplified score rendering in cards and details panel (score value only).

### Removed
- Removed multi-provider rating service (`src/services/rating_service.py`).
- Removed rating-source specific test (`tests/test_rating_source.py`).
- Removed documentation for unused external score env vars (`OMDB_API_KEY`, `MAL_CLIENT_ID`).

### Quality
- Full quality suite passed (`73 passed`, total coverage `84%`).
- Runtime smoke checks passed on source and packaged build (`dist/AiringDeck.exe`).
- Release build and installer generated successfully:
  - `dist/AiringDeck.exe`
  - `dist/AiringDeck-Setup-3.3.0.exe`

## [3.3.0-beta.1] - 2026-02-19

### Added
- Formal prerelease baseline `3.3.0-beta.1`.
- Release/tag process document.
- Official project changelog.

### Quality
- QA suite green (`39 passed`) with total coverage `80%`.
- Dependency scan (`pip-audit`) with no known vulnerabilities.
- Runtime smoke, DPI matrix, E2E, and soak checks passed.

## [3.2.3] - 2026-02-17

### Note
- Last line before formal prerelease governance.
