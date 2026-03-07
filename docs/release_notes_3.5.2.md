# Release v3.5.2

Release date: 2026-03-07

## Highlights

- Safer update baseline with patched network dependency versions.
- Stronger update/install reliability thanks to expanded critical-path tests.
- Standardized release QA process with fixed KPIs and security gates.

## Fixes

- Upgraded `requests` to `2.32.4`, removing previously reported CVE exposure in dependency scans.
- Added automated dependency sync validation between `requirements.txt` and `pyproject.toml`.
- Added CI and local quality-suite gates for `pip-audit` to block vulnerable releases.

## Performance

- No runtime performance regressions observed in quality and smoke runs.

## Compliance (required)

### Data & Privacy impact

- No new personal data collection introduced.
- No changes to No-Tracker behavior or default privacy model.

### Network/API impact

- No AniList endpoint changes.
- Dependency hardening reduces risk in outbound HTTP request handling.

### AniList usage statement

- AiringDeck uses AniList OAuth + GraphQL under AniList terms.
- No-Tracker mode remains active (local viewer model, no AiringDeck cloud tracker backend).

## Upgrade notes

- No manual migration required.
- Existing settings remain compatible.
- Recommended for all users currently on v3.5.1.
