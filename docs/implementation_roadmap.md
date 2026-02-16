# AiringDeck - Piano Aggiunte Future

Ultimo aggiornamento: 16 febbraio 2026

## 1) Stato attuale sintetico

- App desktop Qt/QML con login AniList OAuth.
- Vista calendario settimanale e dettaglio anime.
- Sync asincrona e cache offline base.
- Build Windows con PyInstaller.
- Fallback Python attivo quando l'estensione nativa C non e disponibile.

## 2) Obiettivi prodotto (prossimi step)

1. Stabilizzare UX e rendering (niente regressioni UI).
2. Aggiungere funzioni utili per uso quotidiano (filtri, ordinamenti, azioni rapide).
3. Migliorare affidabilita dati/sync e gestione errori.
4. Alzare qualita tecnica (test, CI, release process).

## 3) Backlog prioritizzato

### P0 - Critico (subito)

- Hardening rendering immagini in sidebar e card con fallback sicuri.
- Migliorare gestione errori rete/token (messaggi specifici per timeout, 401, rate limit).
- Versionamento coerente in UI + build script + metadata package.
- Logging runtime piu chiaro per debug produzione.

### P1 - Alto impatto (breve termine)

- Filtri avanzati: genere, solo oggi, soglia score minima.
- Ordinamenti: airing time, titolo, progresso, score.
- Sidebar dettagli estesi: stagioni, studio, episodi, descrizione pulita.
- Azioni rapide: apri AniList, copia titolo/link.
- Persistenza selezione ultimo anime.

### P2 - Medio termine

- Notifiche desktop per airing imminente.
- Background sync periodica configurabile.
- Modalita offline esplicita (badge/stato dedicato).
- Migrazione cache da solo QSettings a storage strutturato (SQLite).

### P3 - Qualita e distribuzione

- Test unitari su servizi/controller/filtro.
- Test integrazione minimi su flusso login+sync+render.
- CI pipeline (lint + test + build artifact).
- Installer Windows e strategia aggiornamenti.

## 4) Milestone consigliate

### Milestone A (1-2 settimane)

- Chiudere P0.
- Stabilizzare rendering cover e fallback.
- Consolidare log e messaggi errore.

### Milestone B (2-4 settimane)

- Implementare blocco P1 completo.
- Testare UX su dataset reali AniList.

### Milestone C (4-8 settimane)

- Implementare P2 (notifiche + background sync + offline).
- Definire schema dati locale evolutivo.

### Milestone D (continuo)

- P3: test automation + CI + packaging/release.

## 5) Definition of Done per ogni feature

- Nessun freeze UI durante operazioni lunghe.
- Stati loading/error/empty sempre gestiti.
- Comportamento coerente online/offline.
- Copertura test minima per logica critica.
- Build ripetibile con note di rilascio chiare.

## 6) Rischi principali e mitigazioni

- Rischio: regressioni QML su binding complessi.
  - Mitigazione: preferire source semplici, fallback espliciti, smoke test UI per release.
- Rischio: differenze ambiente build (toolchain C mancante).
  - Mitigazione: mantenere fallback Python e profili build chiari.
- Rischio: errori API non gestiti in modo granulare.
  - Mitigazione: normalizzazione errori e retry/backoff centralizzati.

## 7) Criteri obbligatori per entrare in Release Stable (GA)

1. Qualita build/release:
   - build Windows ripetibile in CI su branch release
   - artifact versionato e changelog aggiornato
2. Qualita codice:
   - nessun `P0`/`P1` aperto
   - nessun `except:` naked nei moduli core/services
3. Test minimi obbligatori:
   - unit test core/services verdi
   - smoke test avvio UI/QML verde
4. Stabilita runtime:
   - login/sync/logout funzionanti su account reale
   - rendering immagini card/sidebar con fallback verificato
5. Governance versione:
   - tag Git release creato
   - versione coerente tra `src/version.py`, metadata package e UI
