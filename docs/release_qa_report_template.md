# AiringDeck - Release QA Report Template

Use this template for every release candidate and stable tag.

## 1) Release snapshot
- Version:
- Date (`YYYY-MM-DD`):
- Commit:
- QA owner:

## 2) KPI summary (mandatory)

| KPI | Target | Result | Status |
| --- | --- | --- | --- |
| Total tests passed | `all green` |  |  |
| Coverage total | `>= previous release` |  |  |
| Ruff lint | `0 errors` |  |  |
| Bandit scan | `0 high/medium findings accepted` |  |  |
| Dependency sync check | `PASS` |  |  |
| pip-audit vulnerabilities | `0 known vulnerabilities` |  |  |
| Runtime smoke (`src/main.py`) | `exit code 0` |  |  |
| Build smoke (`dist/AiringDeck.exe`) | `launch + clean auto-exit` |  |  |
| Installer smoke (`AiringDeck-Setup-<version>.exe`) | `install launch successful` |  |  |

## 3) Commands executed
```bash
python scripts/run_quality_suite.py
AIRINGDECK_AUTO_EXIT_MS=12000 python src/main.py
python scripts/build_windows.py
python scripts/build_windows_installer.py --skip-build-exe
```

## 4) Packaging and smoke checklist (mandatory)
- [ ] `dist/AiringDeck.exe` generated for target version.
- [ ] `dist/AiringDeck.exe` runtime smoke passed (auto-exit, no crash).
- [ ] `dist/AiringDeck-Setup-<version>.exe` generated.
- [ ] Installer wizard opens and app launches after install.
- [ ] Update flow smoke validated (check + install/fallback path).
- [ ] No blocking regressions on login/sync/filter/notifications.

## 5) Security and compliance checklist (mandatory)
- [ ] `pip-audit` result attached and clean.
- [ ] Dependency sync check attached and clean.
- [ ] AniList compliance checklist reviewed (`docs/release_compliance_checklist.md`).
- [ ] No-Tracker behavior validated (`docs/manual_no_tracker_checklist.md`).

## 6) Risks and mitigations
- Residual risks:
- Mitigations:
- Deferred items (non-blocking):

## 7) Release decision
- Decision: `GO` / `NO-GO`
- Notes:
