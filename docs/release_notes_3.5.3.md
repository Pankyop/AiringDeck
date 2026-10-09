# Release v3.5.3

Release date: 2026-10-09

## Highlights

- Hardened OAuth local authentication service against network exposure and token leaks.
- Improved updater accuracy by correctly selecting the highest SemVer tag in GitHub fallback.
- Patched dependencies to satisfy automated security audit gates.

## Fixes

- **OAuth Loopback Binding (BUG-01):** Restricted the local TCP OAuth server to loopback interfaces (`127.0.0.1` and `::1`), preventing exposure on external network interfaces.
- **Log Privacy Hardening (BUG-02):** Removed debug log output containing raw request prefixes to prevent bearer tokens from appearing in log files.
- **OAuth Token Integrity (BUG-03):** Eliminated redundant `unquote()` call on query parameters to prevent corruption of percent-encoded token values.
- **Updater Tag Ranking (BUG-04):** Enhanced `_from_tags_payload` to parse and sort all available release tags by SemVer, ensuring the latest version is never missed when tags are not in descending order.

## Dependencies

- Upgraded `requests` to `2.34.2` and `python-dotenv` to `1.2.2` to eliminate vulnerabilities identified by `pip-audit`.

## Compliance (required)

### Data & Privacy impact

- No new personal data collection introduced.
- OAuth token handling is more private and secure against network eavesdropping and debug log leaks.

### Network/API impact

- Binding restricted strictly to local machine loopback.
- Outbound API calls to AniList and GitHub remain unchanged.

### AniList usage statement

- AiringDeck uses AniList OAuth + GraphQL under AniList terms.
- No-Tracker mode remains active (local viewer model, no cloud tracker backend).

## Upgrade notes

- No manual migration required.
- Recommended for all users.
