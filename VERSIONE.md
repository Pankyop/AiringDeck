## 1. EXECUTIVE SUMMARY
AiringDeck e una applicazione desktop end-user (PySide6/QML) per tracking anime con AniList OAuth, sincronizzazione lista “Watching”, calendario settimanale e dettaglio episodio. Dal codice emerge un prodotto usabile e con feature core presenti, ma ancora con gap significativi su test automation, processo release e hardening completo dei flussi UI/rete.

Lo stato reale e **Beta** (non GA), nonostante stringhe UI/metadata riportino “v3.2.2 Stable”. Le funzionalita principali ci sono, l’architettura e modulare (controller + services + model + QML), ma robustezza e qualita ingegneristica non sono ancora al livello “release stabile” per un ciclo affidabile a lungo termine.

Raccomando di adottare **Semantic Versioning (SemVer)** con prerelease formali, mantenendo continuita con la numerazione esistente: partire da **`3.3.0-beta.1`** come prima versione “formalmente gestita”, poi avanzare verso RC e 4.0.0 solo quando esistono test, changelog e policy breaking changes.

## 2. ANALISI DETTAGLIATA DEL PROGETTO
### Analisi tecnica
- Tipo software: app desktop GUI (non libreria/API pubblica), con packaging Windows `.exe`.
- Linguaggi/framework:
  - Python + PySide6 (`src/main.py`, `src/core/*`, `src/services/*`)
  - QML UI (`src/ui/qml/*`)
  - C extension opzionale (`src/core/_airingdeck_native.c`)
- LOC approssimative (solo `src`, `.py/.qml/.c`): ~**2564** linee.
  - Python: 945
  - QML: 1544
  - C: 75
- Componenti principali:
  - `core`: orchestrazione app (`app_controller.py`), model Qt, worker async, fallback/bridge native
  - `services`: OAuth + API AniList
  - `ui/qml`: shell finestra, contenuto principale, componenti
  - `scripts`: build Windows
- Architettura: **modulare monolith desktop** (single-process, separazione UI/logica/servizi).

### Completezza funzionale
Funzioni implementate (evidenze):
- Avvio app + caricamento QML: `src/main.py`
- Login OAuth AniList con callback locale: `src/services/auth_service.py`
- Sync profilo + lista watching AniList GraphQL: `src/services/anilist_service.py`
- Modello dati Qt e binding UI: `src/core/anime_model.py`, `src/core/app_controller.py`
- Calendario settimanale + dettaglio anime + ricerca: `src/ui/qml/MainContent.qml`
- Cache offline base (QSettings): `src/core/app_controller.py`
- Build EXE e tentativo build estensione nativa: `scripts/build_windows.py`

Indicatori di incompletezza:
- Nessuna suite test (`tests` assente).
- TODO/FIXME espliciti quasi assenti, ma ci sono warning/storico instabilita in log (`startup_log.txt`, `startup_error.txt`).
- Versioning/documentazione rilascio non formalizzati (niente `CHANGELOG.md`, pochi commit visibili).

Stima completezza prodotto: **80-85%** (feature complete per uso base, quality/release process incompleti).

### Qualita codice
Punti buoni:
- Struttura modulare chiara.
- Segnali/slot Qt usati correttamente.
- Logging introdotto in punti core (`main`, `app_controller`, `services`).
- Retry/backoff API presenti (`src/services/anilist_service.py`).

Debito tecnico rilevato:
- `Worker.run()` usa `except:` naked e `traceback.print_exc()` (da sostituire con logger + eccezioni esplicite) in `src/core/worker.py`.
- Dipendenze duplicate e non allineate tra `requirements.txt` (pinned) e `pyproject.toml` (range `>=`).
- Versione hardcoded in QML About/Settings (“v3.2.2 Stable”) invece di binding unico a `appVersion`.
- Repository molto “dirty” e storia commit non significativa (solo 1 commit visibile).

### Stabilita e robustezza
- Logging: presente ma non uniforme in tutti i moduli.
- Validazione input:
  - API/OAuth con controlli base presenti.
  - Parsing token con fallback/error handling (`auth_service.py`).
- Potenziali crash/rischi:
  - Thread worker con catch-all non strutturato.
  - Stato UI dipendente da immagini remote (gia emerse regressioni funzionali nei log/screenshot).
- Dipendenze: gestite con pip/pyproject, ma policy versioning mista (strict + loose).

### Interfaccia utente/API
- UI molto avanzata (custom title bar, splash, card, sidebar), non un semplice prototipo.
- Esistono ancora segnali di fragilita su rendering immagini/sidebar (richieste utente ripetute + log storici).
- Hardcoded da rendere configurabili:
  - `CLIENT_ID` AniList in codice (`src/services/auth_service.py`)
  - porte e URI callback
  - stringhe versione “stable” in QML

### Documentazione
- README presente e buono per setup/build (`README.md`).
- Docs tecniche presenti (`docs/native_optimization.md`, `docs/multithreading_analysis.md`, `docs/implementation_roadmap.md`).
- Mancano:
  - changelog ufficiale
  - guida utente finale completa
  - policy versioning/release ufficiale

### Build e distribuzione
- Build automatica locale: `scripts/build_windows.py` + PyInstaller.
- Build nativa C opzionale con fallback Python.
- Installazione dev semplice.
- CI/CD assente (`.github` assente).

### Storia e versioning
- Commit visibili: **1** (`feat: initial Qt project setup`, 2026-02-11).
- Tag: nessuno.
- Pattern versione nel codice: “3.2.2” in piu punti (`src/version.py`, `pyproject.toml`, `setup.py`, QML).
- Conclusione: versioning esiste ma non tracciato formalmente con storia release/tag/changelog.

### Sicurezza
- Gestione dato sensibile: token OAuth, salvato via `keyring` (buona pratica).
- `.env` contiene placeholder (`ANILIST_CLIENT_ID=YOUR_CLIENT_ID_HERE`), nessun secret reale esposto.
- Rischi:
  - OAuth implicit flow + server locale (accettabile per desktop, ma da hardenare/monitorare).
  - Messaggi errore potenzialmente troppo generici in alcuni percorsi.

### Dipendenze ed ecosistema
- Dipendenze principali: PySide6, requests, dotenv, keyring, pyinstaller.
- In generale mature/stabili.
- Non espone API pubbliche per terzi: e principalmente app end-user.

### Target e utilizzo
- Utente target: end-user anime watcher su desktop Windows.
- Rischio bug: **medio** (non safety-critical, ma UX e affidabilita dati impattano molto la percezione).
- Contesto: prodotto reale in maturazione, non solo demo, ma non ancora GA robusta.

## 3. STADIO DI SVILUPPO DETERMINATO
**Stadio scelto: Beta (avanzata).**

Motivazione:
- Core feature disponibili e usabili: login, sync, calendario, dettaglio, ricerca, cache, build exe.
- Mancano asset tipici RC/GA: test suite, changelog/version governance, CI, hardening completo regressioni UI.
- Evidenze di fragilita recente su UI/rendering nei log storici e nel flusso di sviluppo.

Per passare a RC servono:
1. Test minimi automatici (unit + smoke integration).
2. Changelog + tag release + policy versioning.
3. Stabilizzazione definitiva rendering immagini e fallback.
4. Audit error handling thread/network completo.
5. Pipeline CI con lint/test/build.

Stima lavoro al prossimo stadio:
- **2-4 settimane** (1 dev full-time) per arrivare a RC credibile.
- **4-8 settimane** per GA con processo rilascio solido.

## 4. SISTEMA DI VERSIONING RACCOMANDATO
**Scelta: Semantic Versioning (SemVer) + prerelease (`-alpha/-beta/-rc.N`).**

Schema consigliato:
- `MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`
- `MAJOR`: breaking changes utente/compatibilita dati/comportamenti principali.
- `MINOR`: nuove feature backward-compatible.
- `PATCH`: bugfix e hardening senza cambi funzionali incompatibili.

Perche e adatto qui:
- Hai gia una numerazione tipo semantica (`3.2.2`).
- Devi comunicare chiaramente fix vs feature vs breaking changes.
- Anche se e una app (non libreria), SemVer semplifica supporto e release note.

Perche non gli altri:
- CalVer: utile per cadenza temporale, ma comunica peggio impatto tecnico dei cambi.
- Sequential semplice: troppo poco informativo per regressioni/UI/API AniList.
- Hybrid/Marketing: overhead inutile in questo stadio.

## 5. VERSIONE INIZIALE
**Versione consigliata adesso: `3.3.0-beta.1`**

Razionale:
- Mantiene continuita con l’attuale `3.2.2` (evita “downgrade numerico”).
- Segnala che il prossimo ciclo e formalmente in beta (non “stable”).
- Incremento `MINOR` coerente con lavoro strutturale P0/P1 e hardening in corso.

Cosa comunica agli utenti:
- “App usabile, ma ancora in validazione attiva”.
- “Aspettati fix frequenti senza grandi breaking changes nel breve”.

Coerenza ecosistema Python/desktop:
- pienamente coerente con SemVer + prerelease e tool release automation.

## 6. ROADMAP DI VERSIONING
### Prossimi 3-6 mesi
- `3.3.0-beta.1` (subito): baseline versioning formale + changelog.
- `3.3.0-beta.2` (2-3 settimane): fix regressioni UI immagini + error handling worker + test smoke.
- `3.3.0-rc.1` (4-6 settimane): freeze feature, CI attiva, test regressione pass.
- `3.3.0` (6-8 settimane): prima release stabile della linea 3.3.
- `3.3.1` (entro 1-2 settimane da GA): eventuali hotfix post-release.

### 6-12 mesi
- `3.4.x`: miglioramenti funzionali non-breaking (filtri avanzati, background sync, notifiche).
- `3.5.x`: consolidamento offline/storage e performance.
- `4.0.0` solo quando:
  - cambi contratto dati locale/API interna in modo incompatibile,
  - o redesign UX/comportamentale con migrazione utenti.

### Strategia rilascio
- Frequenza consigliata:
  - Beta/RC: ogni 2 settimane.
  - Stable: mensile/trimestrale, patch on-demand.
- Hotfix critici: `X.Y.(Z+1)` entro 24-48h.
- Minor release: `X.(Y+1).0` per feature compatibili.
- Major release: `(X+1).0.0` con piano migrazione e deprecazioni annunciate.

Comunicazione breaking changes:
- Annuncio deprecazione in almeno una minor precedente.
- Sezione “Breaking Changes” obbligatoria in changelog.
- Nota migrazione con passi espliciti.

## 7. ACTION ITEMS PRIORITIZZATI
1. Eliminare `except:` naked in `src/core/worker.py` e uniformare logging errori.
2. Unificare versione in un solo source-of-truth (`src/version.py`) anche in QML About/Settings.
3. Introdurre test minimi:
   - unit su `anilist_service` (retry/error mapping)
   - unit su `app_controller` (state transitions)
   - smoke avvio QML.
4. Aggiungere `CHANGELOG.md` e tag Git per ogni release.
5. Configurare CI (lint + test + build).
6. Allineare policy dipendenze (`requirements.txt` vs `pyproject.toml`) con strategia chiara.
7. Spostare `CLIENT_ID` in config/ENV con fallback sicuro, documentato.

## 8. ESEMPI PRATICI
- Prossimo bugfix (nessuna feature): `3.3.1`
- Prossima feature compatibile (es. nuovo filtro): `3.4.0`
- Breaking change (es. cambio struttura cache incompatibile): `4.0.0`
- Hotfix critico su produzione (da `3.3.0`): `3.3.1`
- Beta incrementale durante validazione: `3.3.0-beta.2`, `3.3.0-beta.3`
- RC incrementale: `3.3.0-rc.1`, `3.3.0-rc.2`

## 9. TEMPLATE DI CHANGELOG
```md
# Changelog
Tutte le modifiche rilevanti sono documentate in questo file.

Il formato segue Keep a Changelog e Semantic Versioning.

## [Unreleased]
### Added
- 
### Changed
- 
### Fixed
- 
### Deprecated
- 
### Removed
- 
### Security
- 

## [3.3.0-beta.1] - 2026-02-16
### Added
- Formalizzazione versioning SemVer con prerelease.
### Changed
- 
### Fixed
- 
### Known Issues
- 

## [3.2.2] - 2026-02-16
### Note
- Versione precedente informalmente marcata come stable nel codice/UI.
```

## 10. COMANDI/CONFIGURAZIONE
### Opzione consigliata (Python): `python-semantic-release`
Installazione:
```bash
pip install python-semantic-release
```

Configurazione minima in `pyproject.toml`:
```toml
[tool.semantic_release]
version_variable = [
  "src/version.py:APP_VERSION",
  "pyproject.toml:project.version",
  "setup.py:version"
]
branch = "master"
changelog_file = "CHANGELOG.md"
build_command = "python scripts/build_windows.py"
commit_parser = "conventional"
```

Convenzione commit (obbligatoria):
- `fix:` -> PATCH
- `feat:` -> MINOR
- `feat!:` o `BREAKING CHANGE:` -> MAJOR

Comandi base:
```bash
semantic-release version
semantic-release publish
```

### Alternativa leggera: `bump2version`
`setup.cfg` esempio:
```ini
[bumpversion]
current_version = 3.3.0-beta.1
commit = True
tag = True

[bumpversion:file:src/version.py]
search = APP_VERSION = "{current_version}"
replace = APP_VERSION = "{new_version}"

[bumpversion:file:pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file:setup.py]
search = version="{current_version}"
replace = version="{new_version}"
```

---

## Assunzioni dichiarate
- La cronologia Git disponibile localmente mostra solo 1 commit; se il repository reale ha storia completa altrove, la valutazione “maturita processo” potrebbe migliorare.
- La valutazione di stabilita include anche segnali storici nei log locali e regressioni osservate durante sviluppo recente.
