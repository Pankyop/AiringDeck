# AiringDeck - Implementation Roadmap

Ultimo aggiornamento: 19 febbraio 2026 (P0 + P1 richiesto completati)

## 1) Stato attuale (reale)

- Versione target: `3.3.0-beta.1`.
- Build Windows: funzionante (`scripts/build_windows.py`, output in `dist/`).
- QA suite: `45 passed`.
- Coverage totale: `80%`.
- Dependency scan (`pip-audit`): PASS.
- Runtime checks senza profiling: smoke, DPI matrix, E2E 3m10s, soak 10m -> PASS.

Conclusione: stato **Beta avanzata**, non ancora GA.

## 2) Avanzamento P0 RC/GA

Stato: **COMPLETATO** (19 febbraio 2026).

Chiusure effettuate:
- `except:` naked rimosso e logging errori uniformato in `src/core/worker.py`.
- Hardcode versione residuo rimosso da UI (About/Settings usano `appController.appVersion`).
- `CHANGELOG.md` ufficiale aggiunto.
- Processo release/tag formalizzato in `docs/release_process.md`.
- Pipeline CI minima aggiunta in `.github/workflows/ci.yml`:
  - `ruff`
  - `bandit`
  - `pytest + coverage`
  - build smoke (`py_compile`)

## 3) Avanzamento P1 richiesto

Stato: **COMPLETATO** (19 febbraio 2026).

Chiusure effettuate:
- Edge case rete/recovery coperti con hardening `AniListService`:
  - retry esplicito su timeout/connection/rate-limit/5xx;
  - stop retry su `401` e su errori GraphQL non transienti.
- Copertura test aggiuntiva su failure path e recovery:
  - nuovi test in `tests/test_anilist_service.py`;
  - nuovi test in `tests/test_integration_controller_flow.py`.
- Accessibilita tastiera/focus migliorata nei componenti QML principali:
  - `activeFocusOnTab`, `KeyNavigation`, `Accessible.*` su header/filtri/card/dialog.
- Policy dipendenze unificata:
  - pin runtime allineati in `requirements.txt` e `pyproject.toml`;
  - policy documentata in `docs/dependency_policy.md`;
  - check automatico `scripts/check_dependency_sync.py` in quality suite/CI.
- Checklist manuale multi-monitor/DPI stabilizzata:
  - `docs/manual_dpi_multimonitor_checklist.md`.

## 4) Gap ancora aperti prima della stable (post-P1)

### P2 - Evoluzione pre/post RC

- Background sync configurabile e resilient scheduling.
- Migrazione storage locale da QSettings a SQLite (schema versionato).
- Installer/update flow Windows (install, uninstall, upgrade testati).

### P3 - Processo e governance

- Protezione branch release + regole merge su CI verde.
- Automazione release notes da changelog/tag.
- Test matrix ampliata (Windows versioni diverse) in CI.

## 5) Roadmap temporale aggiornata

### Fase RC-1 (1-2 settimane)

- Consolidare i miglioramenti P1 su branch release.
- Consolidare CI su branch release.
- Eseguire regression pack completo senza profiling.
- Preparare tag prerelease.

Deliverable:
- `3.3.0-rc.1`
- CI stabile e repeatable

### Fase RC-2 (2-4 settimane)

- Chiudere i P2 prioritari e validazioni manuali bloccanti.
- Hardening finale comportamento runtime.
- Freeze feature.

Deliverable:
- `3.3.0-rc.2` (se necessario) oppure candidatura diretta a `3.3.0`

### Fase GA (4-6 settimane)

- Test finali su build distributiva.
- Verifica installazione/aggiornamento/disinstallazione.
- Pubblicazione stable con changelog e tag finali.

Deliverable:
- `3.3.0` stable

## 6) Definition of Done (obbligatoria)

- Nessun freeze UI nei flussi login/sync/filter/reset.
- Stati loading/error/empty sempre gestiti in UI.
- Nessun `except:` naked nei moduli core/services.
- Suite automatica verde con coverage mantenuto >=80%.
- Versione coerente in `src/version.py`, `pyproject.toml`, `setup.py`, UI.
- Changelog aggiornato e tag Git creato per ogni release.

## 7) Gate GA (stato ad oggi)

1. Build e release process:
- build ripetibile in CI -> **IN CORSO**
- artifact versionato + changelog + tag -> **PARZIALE**

2. Qualita tecnica:
- issue P0 aperte -> **NO** (OK)
- crash bloccanti smoke/E2E/soak -> **NON RILEVATI**

3. Test:
- suite automatica verde -> **OK**
- coverage complessivo >=80% -> **OK**
- regressione UI critica coperta da test/checklist -> **OK** (automatizzato + checklist manuale)

4. Operativita:
- login/sync/logout validati su account reale -> **OK**
- fallback immagini + layout lungo titolo su risoluzioni diverse -> **OK (con validazione manuale da mantenere)**

## 8) Prossima feature consigliata dopo chiusura gate GA

- Background sync intelligente con finestre orarie configurabili e backoff adattivo.
  - Motivo: aumenta utilita quotidiana senza cambiare UX principale.
  - Vincolo: introdurre solo dopo chiusura P2 bloccanti e rilascio `3.3.0` stable.
