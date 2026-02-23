# AniList Compliance Checklist

Last updated: 2026-02-22

This checklist is a practical hardening layer for AiringDeck usage of AniList API.
It is not legal advice.

## AiringDeck API usage summary

- AiringDeck is an unofficial desktop client for personal AniList account usage.
- Authentication is done via AniList OAuth in the user's browser.
- The app reads user-list/schedule data required to show airing episodes and progress.
- AniList account passwords are never handled by AiringDeck.
- By default, no long-term AniList payload cache is stored locally.

## Technical safeguards implemented

- OAuth user-token flow only (no credential scraping).
- Conservative request pacing (`AIRINGDECK_ANILIST_MIN_INTERVAL_SEC`, default `2.1s`).
- Timeout and retry handling for transient failures and HTTP 429.
- Default local AniList data cache disabled (`AIRINGDECK_ANILIST_CACHE_ENABLED=0`).
- Clear client identification via `User-Agent`.

## Required operational steps for "maximum safety"

1. Keep AniList integration read-only for user list synchronization.
2. Do not implement bulk extraction/scraping endpoints.
3. Keep cache disabled unless strictly needed and documented.
4. Contact AniList (`contact@anilist.co`) for written approval if distribution
   could be interpreted as a competing tracker service.
5. Re-check AniList ToS before each public release.

## Suggested email template to AniList

Subject: AiringDeck API usage confirmation request

Hello AniList team,

I maintain AiringDeck, an open-source desktop client that lets users view and
sync their own AniList "CURRENT" anime list using user OAuth tokens.

Current safeguards:
- conservative pacing (<= ~28 requests/min default),
- 429/timeout retry handling,
- no bulk dataset scraping,
- default local cache disabled.

Could you confirm whether this usage is allowed for public distribution?
If needed, I can share repository and release details.

Thanks.
