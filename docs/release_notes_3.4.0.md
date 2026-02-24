# Release v3.4.0

Release date: 2026-02-24

## Highlights

- New Settings menu with a horizontal layout and clearer section structure.
- Removed periodic background sync configuration from Settings.
- Added a manual `Check now` action for on-demand update checks.
- New in-app updater flow: `Update now` downloads and launches the Windows installer directly.

## Fixes

- Test-notification controls are now visible only in dev/test profile mode.
- Improved keyboard navigation and accessibility consistency in update/settings flows.

## Performance

- No expected runtime regressions; Settings UI refresh does not impact calendar performance.

## Compliance (required)

### Data & Privacy impact

- No new remote telemetry was introduced.
- Update download is triggered only by explicit user action.

### Network/API impact

- Update checks still use GitHub Releases/Tags.
- When a Windows installer asset exists in the release, the app uses it directly as update payload.

### AniList usage statement

- AiringDeck uses AniList OAuth + GraphQL under AniList terms.
- No-Tracker mode remains active (local viewer model, no AiringDeck cloud tracker backend).

## Upgrade notes

- Users on previous versions can update from the in-app update notice.
- If a release does not include a Windows installer asset, direct in-app install cannot be started.
