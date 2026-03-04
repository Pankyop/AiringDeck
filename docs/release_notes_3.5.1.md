# Release v3.5.1

Release date: 2026-03-04

## Update type

- `PATCH` release (`3.5.0` -> `3.5.1`).
- No breaking changes.
- Focused on updater reliability and user-facing failure handling.

## Why this update

- Some updater edge cases could still produce ambiguous outcomes for users:
  - unsafe/non-web URLs;
  - unexpected filename values from remote headers;
  - non-installer payload responses from release endpoints.
- This release reduces those risks and improves predictability of the update flow.

## What changes for users

- The in-app updater now accepts only web download links (`http/https`).
- Invalid installer links are rejected safely instead of being executed.
- Fallback behavior is clearer when a direct installer is unavailable.
- Unexpected updater errors now surface a clearer generic message in the UI.

## Fixes

- Hardened installer filename handling during update download.
- Added explicit handling for non-installer payload responses (e.g. JSON/HTML responses).
- Expanded regression coverage for updater hardening scenarios.

## Compliance (required)

### Data & Privacy impact

- No new telemetry introduced.
- Update actions remain user-triggered.

### Network/API impact

- Update checks still use GitHub release/tag metadata.
- Direct installer downloads now enforce safer URL and payload handling.

### AniList usage statement

- AiringDeck uses AniList OAuth + GraphQL under AniList terms.
- No-Tracker mode remains active (local viewer model, no AiringDeck cloud tracker backend).

## Upgrade notes

- Existing users can update normally from `3.5.0`.
- No migration step required for this patch release.
