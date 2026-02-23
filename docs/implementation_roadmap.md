# AiringDeck - Implementation Roadmap

Last updated: February 22, 2026

## 1) Current status

- Current version: `3.3.0` (stable).
- Windows build: OK (`scripts/build_windows.py`, output: `dist/AiringDeck.exe`).
- Windows installer: OK (`scripts/build_windows_installer.py`, output: `dist/AiringDeck-Setup-3.3.0.exe`).
- Quality suite: OK (`73 passed`).
- Total coverage: `84%`.
- Security scan (`bandit`) and dependency policy sync: OK.
- Runtime smoke (source + dist): OK.
- No-Tracker baseline (phases 0-4): implemented locally and validated.

Conclusion: stable release completed and publishable.

## 2) Completed for release 3.3.0

- Core/service hardening (error handling and logging consistency).
- Minimal CI enabled (lint + security + tests + build smoke).
- Changelog and release process formalized.
- Keyboard/focus accessibility improved across key UI components.
- Critical UI layout fixes (long titles, toolbar, details panel).
- Removed multi-provider rating stack and returned to AniList-only scores for stability.

## 3) Post-release backlog (3.3.x)

### P1 - High priority (next cycle)

- Expand coverage for remaining UI/network edge cases.
- Improve coverage in less-exercised `app_controller.py` branches.
- Add automated tests for update flow (accept/dismiss/open link).
- Reduce non-blocking PyInstaller warnings (`pycparser.lextab/yacctab`).

### P2 - Functional evolution

- Configurable background sync (intervals + adaptive backoff).
- Migrate local storage from QSettings to SQLite (versioned schema).
- Improve installer test coverage (install/upgrade/uninstall).

### P3 - Process and release management

- Automate release notes from changelog/tag.
- Expand CI matrix (more Windows/Python environments).
- Enforce release branch policy with mandatory CI gates.

## 4) Suggested version roadmap

- `3.3.1` (patch): post-release fixes and additional test/CI hardening.
- `3.4.0` (minor): background sync + first storage improvements.
- `3.4.1+` (patch): stabilization of the 3.4 line.

## 5) Definition of Done for next releases

- CI green.
- Coverage >= 80%.
- No naked `except:` in core/services.
- Changelog updated.
- Release tag created.
- `dist` build and installer generated without errors.

## 6) No-Tracker implementation status (compliance-first alternative)

Goal: keep AiringDeck useful as an airing viewer while removing behavior that can be interpreted as a third-party tracker product.

### Phase 0 - Product boundary and policy (P0) ✅

- Define and freeze "no-tracker" scope in docs:
  - Read-only schedule browsing.
  - Optional local reminders only.
  - No remote user behavior profiling.
  - No server-side collection owned by AiringDeck.
- Add explicit non-goals:
  - No cross-account tracking dashboard.
  - No central AiringDeck cloud sync for user history.
  - No hidden telemetry by default.
- Deliverables:
  - `docs/product_scope_no_tracker.md`
  - `docs/privacy_data_policy.md`
  - README section "No-Tracker Mode"

Acceptance criteria:
- Feature list and non-goals are documented and consistent across README/docs/app copy.

### Phase 1 - Technical hardening for no-tracker behavior (P0) ✅

- Enforce strict local-data minimization defaults:
  - AniList cache disabled by default (already present, keep as hard default).
  - No long-term storage of full API payloads.
  - Optional short-lived in-memory cache only.
- Ensure all update/network calls are explicit and transparent:
  - Clear user-visible labels for each external call.
  - Conservative rate limiting and retry with backoff.
- Remove/disable any remaining "collector-like" paths:
  - No background bulk sync loops without user action.
  - No analytics identifiers persisted across sessions.

Acceptance criteria:
- Cold restart does not retain full AniList payloads.
- No hidden polling loop runs when app is idle.

### Phase 2 - UX changes to make compliance explicit (P1) ✅

- Add a first-run "Data & Privacy" dialog:
  - Explain exactly what data is requested and why.
  - Separate toggles: reminders, update checks, diagnostics.
- Add "No-Tracker Mode" badge in Settings/About.
- Add "Open on AniList" as primary action for deep interactions.
- Keep user-facing messaging explicit:
  - "AiringDeck is a local viewer, not a cloud tracker."

Acceptance criteria:
- Users can review and disable optional network-adjacent features without editing env vars.

### Phase 3 - Regression and compliance validation (P1) ✅

- Add automated tests:
  - `no_tracker_defaults`: verify strict defaults at startup.
  - `no_payload_persistence`: verify no full payload persistence in settings/cache.
  - `network_transparency`: verify explicit user-triggered refresh path.
  - `rate_limit_backoff`: verify bounded retry behavior.
- Add manual QA checklist:
  - Offline start, reconnect, timeout, intermittent failure, recovery.
  - Privacy settings persistence and opt-out behavior.

Acceptance criteria:
- CI includes no-tracker test set and passes.
- Manual checklist completed for release candidates.

### Phase 4 - Release and governance (P1) ✅

- Publish compliance note with each release:
  - Data flow summary.
  - Third-party API use statement.
  - Changes impacting privacy/network behavior.
- Maintain a lightweight "API compliance review" step before tagging releases.
- Keep AniList usage documentation aligned with their current terms.

Acceptance criteria:
- Release template includes compliance section by default.
- No release is cut without passing compliance checklist.

### Validation snapshot

- New docs added: no-tracker scope + privacy/data policy + release compliance checklist.
- Manual QA checklist added for no-tracker flows and network recovery.
- App controller hardening added: first-run privacy gate, explicit update-check toggle, diagnostics toggle.
- UI updates added: centered privacy dialog, no-tracker badges, "Open on AniList" primary action in details.
- Automated regression tests added for no-tracker defaults and behavior.
