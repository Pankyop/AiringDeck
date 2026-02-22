# Changelog

Tutte le modifiche rilevanti sono documentate in questo file.

Il formato segue Keep a Changelog e Semantic Versioning.

## [Unreleased]

### Changed
- 

### Fixed
- 

### CI
- 

## [3.3.0] - 2026-02-22

### Changed
- Promozione release stabile da `3.3.0-beta.1` a `3.3.0`.
- Rimossa la selezione sorgente voti esterna: l'app usa nuovamente solo score AniList.
- UI semplificata nelle card e nel pannello dettagli (`Voto/Score` senza etichetta provider).

### Removed
- Rimosso il servizio rating multi-provider (`src/services/rating_service.py`).
- Rimosso test specifico rating-source (`tests/test_rating_source.py`).
- Rimosse variabili ambiente non più usate per provider voti esterni (`OMDB_API_KEY`, `MAL_CLIENT_ID`) dalla documentazione.

### Quality
- Quality suite completa passata (`73 passed`, coverage totale `84%`).
- Smoke runtime pass su sorgente e build distribuita (`dist/AiringDeck.exe`).
- Build release e installer generate con successo:
  - `dist/AiringDeck.exe`
  - `dist/AiringDeck-Setup-3.3.0.exe`

## [3.3.0-beta.1] - 2026-02-19

### Added
- Baseline prerelease formale `3.3.0-beta.1`.
- Documento processo release/tag.
- Changelog ufficiale del progetto.

### Quality
- Suite QA verde (`39 passed`) con coverage totale `80%`.
- Dependency scan (`pip-audit`) senza vulnerabilita note.
- Smoke runtime, DPI matrix, E2E e soak test eseguiti con esito positivo.

## [3.2.3] - 2026-02-17

### Note
- Ultima linea pre-prerelease formale.
