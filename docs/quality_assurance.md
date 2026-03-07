# Quality Assurance Workflow

This guide covers:
- Debugging
- Profiling
- Logging/Monitoring
- Testing + Coverage
- Static/Dynamic analysis + Fuzzing

## 1) Full run

```bash
python scripts/run_quality_suite.py --with-profile --profile-duration 30
```

## 2) Detailed runtime profiling

```bash
python scripts/profile_system.py --duration 70 --interval 1.0
```

Output:
- `profiles/system_profile_*.csv`
- `profiles/system_profile_*_summary.txt`

## 3) Tests and coverage

```bash
python -m coverage run -m pytest -q
python -m coverage report -m
```

## 4) Static analysis and security

```bash
python -m ruff check src tests scripts
python -m bandit -q -r src
python scripts/check_dependency_sync.py
python -m pip_audit -r requirements.txt
```

## 5) Fuzzing

`tests/test_fuzz_filter_entries.py` uses `hypothesis` to stress the text filtering path.

## 6) Release KPI report

For every release candidate/stable tag, fill:

- `docs/release_qa_report_template.md`

with fixed KPI fields and packaging/smoke checklist outcomes.
