# Manual No-Tracker QA Checklist

Last updated: 2026-02-22

Use this checklist on release candidates to validate no-tracker behavior.

## Startup and privacy gate

- [ ] Fresh profile: app starts with Data & Privacy dialog centered and blocking background.
- [ ] Before dialog confirmation, no optional network call is triggered.
- [ ] "Save and continue" persists selected preferences.
- [ ] "Use current values" closes the dialog and keeps current toggles.

## Network resilience

- [ ] Offline startup: clear message shown, no crash.
- [ ] Reconnect then sync manually: list fetch succeeds.
- [ ] Timeout/intermittent network: retry path works and returns a readable status message.
- [ ] Rate-limit scenario (429): user-facing message and bounded retry behavior.

## Data persistence boundaries

- [ ] With default settings, AniList payload cache remains disabled.
- [ ] Logout clears runtime list/session state and selected anime details.
- [ ] Privacy toggles remain persisted across restart.

## UX transparency

- [ ] Settings show No-Tracker badge and privacy toggles.
- [ ] About dialog shows No-Tracker mode.
- [ ] Details panel "Open on AniList" opens the selected anime URL.

## Final sign-off

- [ ] No regressions observed in filters, sorting, and details panel.
- [ ] Update modal still works when update checks are enabled.
- [ ] Build smoke passes for `src/main.py` and `dist/AiringDeck.exe`.
