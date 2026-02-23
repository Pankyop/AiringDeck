# Release Compliance Checklist

Last updated: 2026-02-22

Use this checklist before creating any release tag.

## A) Product scope and privacy

- [ ] `docs/product_scope_no_tracker.md` still matches actual behavior.
- [ ] `docs/privacy_data_policy.md` still matches actual behavior.
- [ ] First-run Data & Privacy dialog appears for fresh installs.
- [ ] Optional network features are user-configurable from settings.

## B) Data handling

- [ ] AniList cache default is disabled (`AIRINGDECK_ANILIST_CACHE_ENABLED=0`).
- [ ] No new long-term persistence of full AniList payloads was introduced.
- [ ] Logout still clears runtime session/list state.

## C) Network/API behavior

- [ ] No hidden background polling loops were introduced.
- [ ] AniList request pacing/timeout/429 handling still active.
- [ ] Update checks are disabled when user preference is off.
- [ ] Any new external endpoint is documented in README/docs.

## D) Release communication

- [ ] `CHANGELOG.md` includes privacy/network-impacting changes.
- [ ] Release notes include a "Compliance" section.
- [ ] AniList API statement is present and accurate.

## E) Final go/no-go

- [ ] CI and quality suite are green.
- [ ] Build smoke passes (`src/main.py` + packaged `dist/AiringDeck.exe`).
- [ ] Checklist signed off by maintainer.
