# Quality Assurance Workflow

Questa guida copre:
- Debug
- Profiling
- Logging/Monitoring
- Testing + Coverage
- Static/Dynamic analysis + Fuzzing

## 1) Esecuzione completa

```bash
python scripts/run_quality_suite.py --with-profile --profile-duration 30
```

## 2) Profiling runtime dettagliato

```bash
python scripts/profile_system.py --duration 70 --interval 1.0
```

Output:
- `profiles/system_profile_*.csv`
- `profiles/system_profile_*_summary.txt`

## 3) Test e coverage

```bash
python -m coverage run -m pytest -q
python -m coverage report -m
```

## 4) Analisi statica e sicurezza

```bash
python -m ruff check src tests scripts
python -m bandit -q -r src
```

## 5) Fuzzing

Il file `tests/test_fuzz_filter_entries.py` usa `hypothesis` per stressare il path di filtro testuale.
