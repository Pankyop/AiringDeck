# AiringDeck - Release QA Report

## 1) Release snapshot
- Version: `3.5.2`
- Date: `2026-03-07`
- Commit: local pre-tag snapshot
- QA owner: Codex

## 2) KPI summary

| KPI | Target | Result | Status |
| --- | --- | --- | --- |
| Total tests passed | all green | `106 passed` | PASS |
| Coverage total | >= previous release | `85%` | PASS |
| Ruff lint | 0 errors | PASS | PASS |
| Bandit scan | no blocking findings | PASS | PASS |
| Dependency sync check | PASS | PASS | PASS |
| `pip-audit` vulnerabilities | 0 known vulnerabilities | 0 | PASS |
| Runtime smoke (`src/main.py`) | exit code 0 | PASS | PASS |
| Build smoke (`dist/AiringDeck.exe`) | launch + clean auto-exit | PASS | PASS |
| Installer build (`AiringDeck-Setup-3.5.2.exe`) | generated successfully | PASS | PASS |

## 3) Commands executed
```bash
python scripts/run_quality_suite.py
python scripts/build_windows_installer.py
AIRINGDECK_AUTO_EXIT_MS=10000 dist/AiringDeck.exe
```

## 4) Packaging and smoke checklist
- [x] `dist/AiringDeck.exe` generated for target version.
- [x] `dist/AiringDeck.exe` runtime smoke passed (auto-exit, no crash).
- [x] `dist/AiringDeck-Setup-3.5.2.exe` generated.
- [x] Installer compilation completed via Inno Setup.
- [x] Update flow tests passed in automated integration suite.
- [x] No blocking regressions on login/sync/filter/notifications.

## 5) Security and compliance checklist
- [x] `pip-audit` clean (`No known vulnerabilities found`).
- [x] Dependency sync check clean.
- [ ] Full manual compliance walkthrough to be re-run at final publish checkpoint.
- [ ] Full manual No-Tracker checklist to be re-run at final publish checkpoint.

## 6) Risks and mitigations
- Residual risks:
  - Manual installer UX walkthrough not repeated in this automated cycle.
- Mitigations:
  - Perform a final manual installer open/install/launch verification before broad rollout.
- Deferred items:
  - Further branch coverage improvements in low-frequency `app_controller` paths.

## 7) Release decision
- Decision: `GO` for publishing v3.5.2 release artifacts.
- Notes: quality, dependency security, build, and installer generation gates are green.
