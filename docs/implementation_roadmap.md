# AiringDeck - Implementation Roadmap

Ultimo aggiornamento: 22 febbraio 2026

## 1) Stato attuale

- Versione corrente: `3.3.0` (stable).
- Build Windows: OK (`scripts/build_windows.py`, output in `dist/AiringDeck.exe`).
- Installer Windows: OK (`scripts/build_windows_installer.py`, output in `dist/AiringDeck-Setup-3.3.0.exe`).
- Quality suite: OK (`73 passed`).
- Coverage totale: `84%`.
- Security scan (`bandit`) e dependency policy sync: OK.
- Smoke runtime (source + dist): OK.

Conclusione: release stabile completata e pubblicabile.

## 2) Completato per la release 3.3.0

- Hardening core e servizi (error handling e logging uniformati).
- CI minima attiva (lint + security + test + build smoke).
- Changelog e processo release formalizzati.
- Accessibilita base tastiera/focus estesa nei componenti principali.
- Correzioni layout/UI critiche (titoli lunghi, toolbar, pannello dettagli).
- Rimozione stack rating multi-provider: ritorno a sola fonte AniList per stabilita.

## 3) Backlog post-release (3.3.x)

### P1 - Alta priorita (prossimo ciclo)

- Estendere test su edge case UI/rete residui.
- Migliorare copertura su `app_controller.py` nelle branch meno battute.
- Aggiungere test automatici su update flow (accept/dismiss/open link).
- Ridurre warning PyInstaller non bloccanti (`pycparser.lextab/yacctab`).

### P2 - Evoluzione funzionale

- Background sync programmabile (intervalli + backoff adattivo).
- Migrazione storage locale da QSettings a SQLite (schema versionato).
- Miglioramento install/upgrade/uninstall tests sull'installer.

### P3 - Processo e release management

- Automazione release notes da changelog/tag.
- Matrix CI ampliata (piu ambienti Windows / Python).
- Policy branch release con gate CI obbligatorio.

## 4) Roadmap versioni suggerita

- `3.3.1` (patch): bugfix post-release e hardening test/CI.
- `3.4.0` (minor): background sync + primi miglioramenti storage.
- `3.4.1+` (patch): stabilizzazione della linea 3.4.

## 5) Definition of Done per prossime release

- CI verde.
- Coverage >= 80%.
- Nessun `except:` naked nei moduli core/services.
- Changelog aggiornato.
- Tag release creato.
- Build `dist` e installer generati senza errori.
