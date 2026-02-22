# VERSIONE - Stato Release

Ultimo aggiornamento: 22 febbraio 2026

## Versione corrente

- `3.3.0` (Stable)

File allineati:
- `src/version.py`
- `pyproject.toml`
- `setup.py`

## Gate release eseguiti

1. Quality suite completa:
- Comando: `python scripts/run_quality_suite.py`
- Esito: **PASS**
- Risultati: `73 passed`, coverage totale `84%`

2. Smoke runtime da sorgente:
- Comando: `AIRINGDECK_AUTO_EXIT_MS=12000 python src/main.py`
- Esito: **PASS**

3. Build Windows:
- Comando: `python scripts/build_windows.py`
- Esito: **PASS**
- Output: `dist/AiringDeck.exe`

4. Smoke runtime su build dist:
- Avvio `dist/AiringDeck.exe` con auto-exit
- Esito: **PASS**

5. Build installer Windows:
- Comando: `python scripts/build_windows_installer.py --skip-build-exe`
- Esito: **PASS**
- Output: `dist/AiringDeck-Setup-3.3.0.exe`

## Modifiche chiave incluse nella release

- Consolidamento qualità e processo release (CI + changelog + release process).
- Rimozione completa della feature "fonte voti esterna" e ritorno a sola fonte AniList.
- Semplificazione UI voto (nessuna etichetta provider).
- Pulizia codice/ruoli model legati ai provider rating esterni.

## Artefatti pronti per pubblicazione

- `dist/AiringDeck.exe`
- `dist/AiringDeck-Setup-3.3.0.exe`

## Prossimo ciclo consigliato

- `3.3.1` patch (hardening post-release e ulteriore copertura test su branch `app_controller.py`).
