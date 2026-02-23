# AiringDeck Privacy and Data Policy

Last updated: 2026-02-22

This document describes what data AiringDeck processes and why.
It is a technical policy document and not legal advice.

## Data categories

### 1) Authentication data

- AniList OAuth access token.
- Purpose: call AniList GraphQL APIs on behalf of the signed-in user.
- Storage: handled by local auth/keyring service.

### 2) AniList content data

- Anime titles, genres, cover URLs, progress, next airing metadata, score.
- Purpose: render calendar and details UI.
- Storage: in-memory runtime model.
- Local persistence: disabled by default (`AIRINGDECK_ANILIST_CACHE_ENABLED=0`).

### 3) Local app preferences

- UI language, filter state, sorting, notification preferences, update-check preference, diagnostics preference.
- Purpose: preserve user UX choices between sessions.
- Storage: local `QSettings` key-value store.

### 4) Update metadata

- Latest release/tag metadata from GitHub (version, notes, URL).
- Purpose: show update notice when a newer version exists.
- Control: user can disable update checks in privacy settings.

## What AiringDeck does not do

- It does not send analytics data to an AiringDeck cloud service.
- It does not aggregate multi-user tracking data on remote servers.
- It does not enable hidden telemetry by default.

## User controls

- Upcoming episode notifications: on/off.
- Update checks: on/off.
- Diagnostics mode: on/off (local behavior and logs only).
- Logout clears runtime anime/session state.

## Operational safeguards

- Conservative AniList request pacing and timeout controls.
- Retry handling for transient network failures and HTTP 429.
- No default long-term storage of complete AniList payloads.

## Compliance maintenance

For public releases, maintain:

1. AniList API terms review.
2. No-Tracker checklist verification.
3. Release notes section for privacy/network-impacting changes.
