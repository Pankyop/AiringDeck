# AiringDeck No-Tracker Product Scope

Last updated: 2026-02-22

## Purpose

AiringDeck is a local desktop viewer for anime airing schedules and user-owned AniList list data.
The product goal is to provide a fast local UX, not a centralized tracking platform.

## In-scope behavior

- Read-only schedule browsing from AniList user-authorized data.
- Local filtering, sorting, and countdown rendering.
- Optional local notifications for upcoming episodes.
- Optional update checks against GitHub releases/tags.
- Optional diagnostics logging for local troubleshooting.

## Explicit non-goals

- No AiringDeck cloud backend storing user anime history.
- No centralized cross-account tracking dashboards.
- No hidden telemetry by default.
- No bulk extraction/scraping workflows.
- No remote analytics identifiers persisted across sessions.

## Data handling boundaries

- AniList OAuth token is used only for user-authorized API calls.
- AniList payload persistence is disabled by default.
- App state is stored locally with minimal settings keys.
- No personal data is sent to AiringDeck-owned servers.

## Network transparency principles

- External calls must be user-visible or user-configurable.
- First-run privacy preferences are shown before optional network checks.
- Optional calls (update checks, diagnostics uploads if ever added) are opt-in or clearly toggleable.

## Release gate for No-Tracker mode

Before each release:

1. Verify no hidden background polling loops were introduced.
2. Verify AniList cache default remains disabled.
3. Verify privacy toggle defaults and first-run dialog behavior.
4. Verify docs and in-app text still match real behavior.
