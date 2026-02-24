# Test Report Completo - AiringDeck

Ultimo aggiornamento: 2026-02-18

## 1) Obiettivo del report
Questo documento raccoglie i test eseguiti fin dall'inizio delle attività recenti, con:
- cosa verifica ogni test,
- impatto/comportamento atteso dell'app,
- risultato ottenuto.

## 2) Stato attuale sintetico
- Build: OK (`dist/AiringDeck.exe` generato)
- Suite QA senza profiling: OK
- Test totali correnti: **31 passed**
- Coverage totale corrente: **72%**
- Nessun crash bloccante emerso nei test automatici e nei run runtime estesi.

## 3) Test eseguiti (storico funzionale)

### 3.1 Compile / Build checks
- Comando: `python -m py_compile ...` + `python scripts/build_windows.py`
- Cosa fanno: verificano sintassi Python e compilazione completa (estensione nativa + packaging EXE).
- Comportamento app: build completa, artefatto eseguibile pronto.
- Risultato: **PASS**.

### 3.2 Static analysis (lint + sicurezza)
- `ruff check src tests scripts`
- `bandit -q -r src`
- Cosa fanno: qualità statica codice e ricerca pattern di vulnerabilità comuni.
- Comportamento app: nessuna regressione da issue statiche bloccanti.
- Risultato: **PASS**.

### 3.3 Unit tests (core/services/model/native)
Eseguiti e ampliati su:
- `tests/test_anime_model.py`
- `tests/test_native_accel.py`
- `tests/test_auth_service.py`
- `tests/test_anilist_service.py`
- `tests/test_worker.py`
- `tests/test_ui_localization.py`

Cosa verificano:
- modello QML e ruoli dati,
- filtro nativo/fallback Python,
- auth token/keyring/callback,
- query AniList (successo/errori/retry/timeout/connection),
- worker success/error signals,
- localizzazione IT/EN e update testo UI.

Comportamento app osservato:
- gestione robusta degli errori rete/auth,
- fallback funzionante,
- nessun crash in condizioni normali/unitarie.

Risultato: **PASS**.

### 3.4 Integration tests (controller + servizi + modello)
File: `tests/test_integration_controller_flow.py`

Casi coperti:
- auth completata -> sync -> popolamento modelli,
- filtri/sort end-to-end,
- `HTTP401` -> logout + stato/UI reset,
- `ConnectionError` -> messaggio rete senza logout,
- errore inatteso -> messaggio generico.

Comportamento app osservato:
- trovato e corretto bug di stale UI su logout,
- dopo fix il reset modello è coerente.

Risultato: **PASS**.

### 3.5 System test (senza profiling)
Comando: `python scripts/run_quality_suite.py`

Include:
- compile checks,
- ruff,
- bandit,
- pytest + coverage report.

Risultato finale più recente:
- **31 passed**
- Coverage totale **72%**
- Tutti i check: **PASS**.

### 3.6 Smoke test runtime
Comando tipico:
- `AIRINGDECK_AUTO_EXIT_MS=12000 python src/main.py`

Cosa fa:
- avvio reale app, bootstrap UI, auto-uscita controllata.

Comportamento app:
- startup corretto,
- login/sync attivi se token presente,
- uscita pulita.

Risultato: **PASS**.

### 3.7 Sanity test su fix mirato
Caso: fix logout su errore `HTTP401`.
- Comando: `pytest tests/test_integration_controller_flow.py -k http401`
- Cosa verifica: bug fix specifico effettivamente risolto.
- Risultato: **PASS**.

### 3.8 End-to-End runtime esteso
Run eseguito: ~3m10s con notifica test intermedia.

Cosa verifica:
- flusso reale login/sync/notifica/logout/re-login.

Comportamento app osservato:
- OAuth ok,
- sync ripetuti ok,
- notifica test dispatch ok,
- logout/re-login ok,
- nessun crash.

Risultato: **PASS**.

### 3.9 Startup performance test (benchmark)
5 avvii consecutivi (BootShell):
- 470ms, 485ms, 476ms, 488ms, 536ms
- media 491ms, mediana 485ms

Interpretazione:
- startup stabile sotto ~0.55s nei run misurati.

Risultato: **PASS**.

### 3.10 Load / Stress test sintetico
Scenario:
- dataset sintetico da 5000 anime,
- 80 cicli x 7 operazioni (filtri/sort/reset/search),
- 560 operazioni totali.

Metriche:
- load iniziale: 65.41ms
- tempo totale operazioni: 2127.35ms
- media operazione: 3.799ms

Comportamento app:
- stabile, nessuna eccezione/crash.

Risultato: **PASS**.

### 3.11 Soak test (runtime lungo)
Scenario:
- 10 minuti continui,
- notifica test durante run,
- interazioni utente in sessione.

Comportamento app:
- nessun freeze/crash,
- sync periodici ok,
- uscita timer pulita.

Risultato: **PASS**.

### 3.12 Timeout / Retry / Offline test
Copertura:
- timeout con retry,
- connection error offline con retry,
- mappatura HTTP429,
- mappatura HTTP401 + logout controller.

Comportamento app:
- messaggi utente coerenti,
- nessun crash,
- session handling corretto.

Risultato: **PASS**.

### 3.13 Exception handling + fault injection
Casi:
- keyring failure,
- payload GraphQL con `errors`,
- errore inatteso controller.

Comportamento app:
- fallback e messaggi robusti,
- nessun blocco applicativo.

Risultato: **PASS**.

## 4) Coverage corrente (dettaglio principale)
Dal run più recente della quality suite:
- Totale: **72%** (`TOTAL 1060 stmts, 292 miss`)

Punti principali:
- `src/core/app_controller.py`: 77%
- `src/services/anilist_service.py`: 88%
- `src/services/auth_service.py`: 65%
- `src/core/worker.py`: 100%
- `src/main.py`: 0% (area ancora da coprire)

## 5) Comportamento complessivo dell'app nei test
L'app risulta:
- stabile su flussi standard e condizioni errore simulate,
- robusta su auth/rete/retry/fallback,
- coerente dopo fix logout,
- performante nello startup e sotto carico sintetico.

Rischio residuo principale:
- copertura insufficiente su `src/main.py` (bootstrap path non ancora testato con unit test dedicati).

## 6) Riferimenti artefatti profilo (storico)
Sono presenti numerosi profili già raccolti in `profiles/` (dev + system), tra cui:
- `profiles/system_profile_20260217_202233_summary.txt`
- `profiles/system_profile_20260217_170831_summary.txt`
- `profiles/dev_profile_20260217_171652_cum.txt`
- `profiles/dev_profile_20260217_171652_self.txt`

Nota: in questo report i risultati principali richiesti sono quelli dei test senza profiling e delle esecuzioni runtime/soak/load già effettuate.

## 7) Aggiornamento test successivo (2026-02-18)

### 7.1 Dependency Scan (nuovo)
- Strumento: `pip-audit`
- Comando: `python -m pip_audit -r requirements.txt`

Cosa verifica:
- vulnerabilità note nelle dipendenze Python dichiarate.

Risultato:
- **FAIL (vulnerabilità trovate)**
- Pacchetto impattato: `requests==2.31.0`
- CVE rilevate:
  - `CVE-2024-35195` (fix: `2.32.0`)
  - `CVE-2024-47081` (fix: `2.32.4`)

Comportamento app:
- l'app funziona correttamente nei test funzionali,
- ma la postura sicurezza dipendenze non è conforme a uno standard "stable" finché la dipendenza non viene aggiornata.

Azione consigliata:
- aggiornare `requests` almeno a `2.32.4` (o più recente stabile) in `requirements.txt` e allineare eventuali lock/version metadata.

### 7.2 Fuzzing esteso (nuovo)
- Comando: `HYPOTHESIS_MAX_EXAMPLES=5000 pytest tests/test_fuzz_filter_entries.py`

Cosa verifica:
- robustezza del filtro rispetto a input casuali/malformati su molte combinazioni.

Risultato:
- **PASS** (`1 passed`)

Comportamento app:
- nessun crash, nessuna divergenza rispetto al riferimento Python nel caso testato.

### 7.3 Stato complessivo dopo aggiornamento
- Qualità funzionale/robustezza runtime: positiva (test passati)
- Sicurezza dipendenze: **da correggere** (2 CVE su `requests`)
- Coverage totale invariata rispetto all'ultimo run QA completo: **72%**

## 8) Remediation sicurezza dipendenze (2026-02-18)

Azione eseguita:
- `requests` aggiornato da `2.31.0` a `2.32.4` in:
  - `requirements.txt`
  - `pyproject.toml`

Verifica post-fix:
- `pip-audit -r requirements.txt` -> **No known vulnerabilities found**

Regressione post-fix:
- Test rete/integration mirati -> **12 passed**
- Suite QA senza profiling -> **31 passed**
- Coverage totale invariata -> **72%**

Conclusione:
- Le CVE rilevate su `requests` sono state risolte.
- Nessuna regressione funzionale introdotta dal bump dipendenza.

## 9) Nuovo blocco test: Main bootstrap / entrypoint (2026-02-18)

Test aggiunti:
- `tests/test_main_bootstrap.py`

Cosa verificano:
- parsing truthy env (`_is_truthy`),
- errore init controller (`Init Error`) gestito,
- errore risorsa QML mancante (`Resource Error`) gestito,
- errore engine senza root objects (`QML Error`) gestito,
- scheduling timer (`AIRINGDECK_AUTO_EXIT_MS`, `AIRINGDECK_TEST_NOTIFICATION_MS`) e nome app in profilo.

Issue incontrata durante sviluppo test:
- patching di `os.name` causava internal error pytest su Windows (`PosixPath` su piattaforma NT).
- risolto rimuovendo quel patch e mantenendo test isolati con mock Qt.

Risultati finali:
- `tests/test_main_bootstrap.py`: **5 passed**
- Suite QA senza profiling: **36 passed**

Impatto su coverage:
- `src/main.py`: **84%** (prima 0%)
- Coverage totale progetto: **78%** (prima 72%)

Comportamento app dai test:
- bootstrap più robusto e verificato su percorsi di errore principali,
- nessuna regressione funzionale introdotta.

## 10) Concurrency test (2026-02-18)

Test aggiunti:
- `tests/test_concurrency_controller.py`

Cosa verificano:
- `syncAnimeList()` concorrenti con completamento interleaved (ordine non sequenziale),
- modifica filtri mentre un sync è pendente,
- mutazioni UI state (onlyToday/sort/reset) durante sync pendenti.

Comportamento app osservato:
- nessun crash o deadlock,
- stato coerente dopo completamento worker,
- modelli/daily counts rimangono validi.

Risultati:
- Test concorrenza dedicati: **3 passed**
- Suite completa senza profiling: **39 passed**

Coverage aggiornato:
- Totale progetto: **80%**
- `src/core/app_controller.py`: **79%**
- `src/main.py`: **84%**

Conclusione:
- comportamento concorrente nel perimetro testato è stabile,
- qualità complessiva aumentata e soglia coverage >=80% raggiunta.

## 11) Accessibility + DPI/Multi-monitor (2026-02-19)

### 11.1 Parte automatizzata eseguita

Audit statico QML:
- Ricerca pattern accessibilità/focus (`Accessible.*`, `focusPolicy`, `KeyNavigation`, `activeFocusOnTab`).
- Esito: **NO_MATCHES** (nessuna annotazione esplicita trovata nel QML corrente).

DPI runtime stability test:
- Avvio app con `QT_SCALE_FACTOR`:
  - `1.0` -> exit code 0
  - `1.25` -> exit code 0
  - `1.5` -> exit code 0
- In tutti i run: avvio/login/sync completati senza crash.

Comportamento app osservato:
- stabile al variare dello scaling (nessun crash/freeze nel perimetro testato),
- bootstrap e sincronizzazione funzionanti.

### 11.2 Parte manuale residua (non automatizzabile in modo affidabile qui)
- verifica visiva testi tagliati/overlap su 100/125/150%,
- verifica contrasto reale delle tendine su monitor diversi,
- verifica navigazione completa da tastiera (tab order/focus visivo),
- verifica con screen reader.

Stato:
- Automated accessibility/DPI stability: **PASS**
- Accessibility UX completa: **richiede validazione manuale**

## 12) Compatibilità automatizzata aggiuntiva (2026-02-19)

Eseguito autonomamente:
- DPI runtime matrix con notifica test su:
  - `QT_SCALE_FACTOR=1.0`
  - `QT_SCALE_FACTOR=1.25`
  - `QT_SCALE_FACTOR=1.5`
- Timer: auto-exit 20s, test notification 8s.

Risultati:
- Tutti i run: `exit_code=0`
- Login/sync/notifica: eseguiti correttamente in ogni run
- Nessun crash/freeze osservato nel perimetro automatico

Audit accessibilità statico QML:
- ricerca di proprietà esplicite (`Accessible.*`, `focusPolicy`, `KeyNavigation`, `activeFocusOnTab`)
- esito: nessun match esplicito nel codice QML corrente

Nota log:
- `startup_log.txt` contiene anche errori storici di run precedenti (QML parse error su vecchio `main.qml`), non riprodotti nei run compatibilità recenti.

## 13) Aggiornamento P1 (2026-02-19)

### 13.1 Edge case rete/recovery (nuovo)

Aggiornamenti implementati:
- Hardening retry in `src/services/anilist_service.py` su errori transienti:
  - timeout
  - connection error
  - HTTP429
  - HTTP5xx
- Stop retry su errori non transienti:
  - HTTP401
  - errori GraphQL payload

Nuovi test:
- `tests/test_anilist_service.py`
  - recovery dopo timeout intermittente
  - recovery dopo HTTP429 intermittente
  - nessun retry su HTTP401
- `tests/test_integration_controller_flow.py`
  - mapping messaggio timeout
  - mapping messaggio rate limit
  - recovery controller dopo sync fallita transientemente

Risultato:
- test mirati P1: **18 passed**
- suite completa senza profiling: **45 passed**

### 13.2 Accessibilita tastiera/focus (nuovo)

Aggiornamenti QML principali:
- `activeFocusOnTab`, `KeyNavigation`, `Accessible.*` su:
  - ricerca/sync/login
  - filtri/sort/reset
  - card anime cliccabili
  - pulsanti principali dei dialog

Verifica runtime:
- smoke startup post-modifica QML: **PASS** (nessun errore caricamento)

### 13.3 Policy dipendenze unificata (nuovo)

Aggiornamenti:
- dipendenze runtime allineate e pin in:
  - `requirements.txt`
  - `pyproject.toml`
- policy documentata:
  - `docs/dependency_policy.md`
- check automatico sync:
  - `scripts/check_dependency_sync.py`
  - integrato in `scripts/run_quality_suite.py`
  - integrato in `.github/workflows/ci.yml`

Risultato:
- dependency sync check: **PASSED**

### 13.4 Checklist multi-monitor/DPI stabilizzata (nuovo)

Documento aggiunto:
- `docs/manual_dpi_multimonitor_checklist.md`

Contenuto:
- matrice scaling/risoluzione/monitor
- checklist UI per header, card, sidebar, dialog
- checklist tastiera/focus
- criteri accettazione + evidenze screenshot richieste

### 13.5 Coverage corrente dopo update P1

Dal run quality più recente:
- Totale: **80%** (`TOTAL 1069 stmts, 219 miss`)
- Test passati: **45 passed**
