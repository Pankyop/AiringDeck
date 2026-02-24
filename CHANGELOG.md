# Changelog

All notable changes to this project are documented in this file.

This project follows Keep a Changelog and Semantic Versioning.

## [Unreleased]

### Changed
- No pending entries.

## [3.4.0] - 2026-02-24

### Added
- In-app updater flow: `Update now` downloads the Windows installer and starts it directly.
- Release feed parsing now prefers Windows installer assets from GitHub releases.
- Update modal now shows installer progress/state messages during update start.

### Changed
- Settings dialog redesign with a horizontal layout and refreshed section structure.
- Removed background sync configuration and related periodic sync behavior from settings.
- Added manual `Check now` action in settings for on-demand update checks.
- Kept test-only controls hidden from normal app profile builds.

## [3.3.0] - 2026-02-23

### Added
- First public stable release of AiringDeck.
- Native desktop app (PySide6/QML) with AniList OAuth integration.
- Airing calendar view, progress tracking, and episode countdown details.
- No-Tracker mode baseline with local-first behavior and privacy-focused defaults.
- Automated update notification support from GitHub releases.
- Windows installer package published in release assets:
  - `AiringDeck-Setup-3.3.0.exe`

### Changed
- Project license aligned to `GPL-3.0-or-later`.
- AniList API usage/compliance documentation clarified.
- Installer flow updated with mandatory license acceptance and AniList API notice.

### Notes
- This changelog is aligned with the current GitHub Releases page, where only `v3.3.0` is published.
