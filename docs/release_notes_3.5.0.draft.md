# Release v3.5.0 (Draft)

Release date: TBD

## Highlights

- SQLite storage migration (schema v1) for local app settings/state.
- Hardened in-app updater flow with clearer fallback/error handling.
- Expanded automated coverage for migration and installer update paths.

## User-visible changes

- More resilient update experience with clearer status feedback.
- Automatic fallback to release page when direct installer asset is unavailable.
- Stable behavior when installer download or launch cannot be completed.
- Backward-compatible migration from existing settings.

## Compliance (required)

### Data & Privacy impact

- No new remote telemetry planned.
- Update actions remain user-initiated.

### Network/API impact

- Update checks remain GitHub-based.
- No additional AniList data collection paths planned.

### AniList usage statement

- AiringDeck uses AniList OAuth + GraphQL under AniList terms.
- No-Tracker mode remains active (local viewer model, no AiringDeck cloud tracker backend).

## Upgrade notes

- Existing users should migrate settings automatically on first launch.
- Rollback/fallback behavior must be documented before release finalization.
