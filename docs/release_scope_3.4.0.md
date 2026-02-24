# AiringDeck - Release Scope Freeze 3.4.0

Last updated: 2026-02-24

## 1) Goal

Define and lock the implementation scope for release `3.4.0` as a `MINOR`
SemVer increment: new backward-compatible features, no breaking changes.

## 2) Baseline and timing

- Current stable version: `3.3.0`.
- Target version: `3.4.0`.
- Scope freeze date: `2026-02-25`.
- Planned release window: week of `2026-03-02`.

## 3) Scope candidates and decision

### IN (approved for 3.4.0)

1. Manual on-demand "Check now" action in settings for update checks.
2. First storage migration step from `QSettings` to `SQLite` (schema v1).
3. Automated test coverage for update flow (accept/dismiss/open release link).

### OUT (deferred beyond 3.4.0)

1. Any breaking change in public or internal app behavior.
2. Large architectural refactors not required by the 3.4.0 IN scope.
3. Non-essential feature expansion not tied to the three approved items.
4. CI matrix expansion and release branch policy enforcement (process track).
5. Installer lifecycle deep tests (install/upgrade/uninstall) unless needed to
   unblock a release-critical defect.

## 4) Acceptance criteria by IN item

### 4.1 Manual on-demand update check in settings

- Add a "Check now" button in the settings update section.
- The button triggers the existing `checkForUpdates` flow.
- Behavior remains transparent and user-initiated (no hidden periodic polling).
- Existing startup update-check toggle remains unchanged.
- Keyboard navigation and accessibility stay consistent with existing controls.

### 4.2 QSettings to SQLite step 1 (schema v1)

- Introduce SQLite storage with explicit schema versioning (`v1`).
- One-shot startup migration path from existing `QSettings` values.
- Migration is idempotent (safe on repeated startup).
- App remains backward-compatible for current users; no data-loss regression.
- Tests added for first-run migration, repeated startup, and fallback behavior.

### 4.3 Update flow automated tests

- Add tests for update notice actions:
  - accept/update now action;
  - dismiss action;
  - open release link action.
- Validate integration path from service payload to controller/UI action handling.
- Ensure existing update payload compatibility (`release` and `tag` sources).

## 5) Definition of Done for Scope Freeze (Point 1)

Point 1 is complete when all conditions below are true:

1. `IN/OUT` scope is documented and approved in this file.
2. Every IN item has explicit acceptance criteria.
3. Exclusions are clear enough to reject scope creep during implementation.
4. Risks and dependencies are listed with owner and mitigation.

## 6) Risks, dependencies, and mitigations

- Risk: migration edge cases from legacy settings values.
  - Mitigation: add fixtures for malformed/missing legacy keys and recovery path.
- Risk: repeated manual triggers can increase unnecessary network calls.
  - Mitigation: keep existing `checkForUpdates` gating and status messaging.
- Dependency: test harness updates may be needed for controller/UI flow coverage.
  - Mitigation: prioritize test scaffolding before feature merge.

## 7) Change control during freeze

- Any new candidate item defaults to OUT unless explicitly approved.
- Approval requires:
  1. written rationale;
  2. impact on release date;
  3. added/updated acceptance criteria.
- All approved changes must be logged in the table below.

| Date       | Proposal | Decision | Impact | Owner |
|------------|----------|----------|--------|-------|
| 2026-02-24 | Initial 3.4.0 scope freeze | Approved | Baseline scope | Team |

## 8) Related documents

- `docs/implementation_roadmap.md`
- `docs/release_process.md`
- `docs/release_compliance_checklist.md`
- `docs/release_notes_template.md`
