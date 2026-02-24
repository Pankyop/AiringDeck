# AiringDeck - Congelamento Scope Release 3.4.0

Ultimo aggiornamento: 2026-02-24

## 1) Obiettivo

Definire e bloccare lo scope di implementazione della release `3.4.0` come
incremento SemVer `MINOR`: nuove funzionalita compatibili all'indietro, senza
breaking changes.

## 2) Baseline e tempistiche

- Versione stabile corrente: `3.3.0`.
- Versione target: `3.4.0`.
- Data freeze scope: `2026-02-25`.
- Finestra release pianificata: settimana del `2026-03-02`.

## 3) Candidati di scope e decisione

### IN (approvati per 3.4.0)

1. Azione manuale "Controlla ora" in impostazioni per verifica update on-demand.
2. Primo step di migrazione storage da `QSettings` a `SQLite` (schema v1).
3. Copertura test automatica per update flow (accept/dismiss/open release link).

### OUT (rinviati oltre la 3.4.0)

1. Qualsiasi breaking change nel comportamento pubblico o interno dell'app.
2. Refactor architetturali ampi non richiesti dallo scope IN della 3.4.0.
3. Espansioni funzionali non essenziali non legate ai tre item approvati.
4. Espansione matrice CI ed enforcement policy release branch (traccia processo).
5. Test approfonditi ciclo installer (install/upgrade/uninstall), salvo blocchi
   critici per la release.

## 4) Criteri di accettazione per item IN

### 4.1 Verifica update manuale on-demand in impostazioni

- Aggiungere pulsante "Controlla ora" nella sezione update delle impostazioni.
- Il pulsante deve invocare il flusso `checkForUpdates` esistente.
- La verifica resta trasparente e user-initiated (nessun polling periodico nascosto).
- Il toggle "Controllo aggiornamenti all'avvio" resta invariato.
- Navigazione tastiera e accessibilita coerenti con i controlli esistenti.

### 4.2 Da QSettings a SQLite step 1 (schema v1)

- Introdurre storage SQLite con versionamento esplicito schema (`v1`).
- Percorso di migrazione one-shot all'avvio dai valori `QSettings` esistenti.
- Migrazione idempotente (sicura su avvii ripetuti).
- Compatibilita all'indietro mantenuta per utenti correnti, senza regressioni
  di perdita dati.
- Aggiunti test per prima migrazione, avvio ripetuto e fallback.

### 4.3 Test automatizzati update flow

- Aggiungere test per azioni su update notice:
  - azione accept/update now;
  - azione dismiss;
  - azione open release link.
- Validare il percorso integrato da payload service a gestione controller/UI.
- Garantire compatibilita con payload update esistenti (sorgenti `release` e
  `tag`).

## 5) Definition of Done per Scope Freeze (Punto 1)

Il Punto 1 e completato quando tutte le condizioni seguenti sono vere:

1. Scope `IN/OUT` documentato e approvato in questo file.
2. Ogni item IN ha criteri di accettazione espliciti.
3. Le esclusioni sono sufficientemente chiare da bloccare scope creep.
4. Rischi e dipendenze sono elencati con owner e mitigazione.

## 6) Rischi, dipendenze e mitigazioni

- Rischio: edge case di migrazione da valori legacy settings.
  - Mitigazione: aggiungere fixture per chiavi legacy mancanti/malformate e
    percorso di recovery.
- Rischio: trigger manuali ripetuti possono aumentare chiamate non necessarie.
  - Mitigazione: mantenere gating esistente su `checkForUpdates` e messaggi stato.
- Dipendenza: possono servire aggiornamenti al test harness per coprire
  controller/UI flow.
  - Mitigazione: prioritizzare test scaffolding prima del merge feature.

## 7) Change control durante il freeze

- Ogni nuovo item candidato e OUT di default, salvo approvazione esplicita.
- L'approvazione richiede:
  1. razionale scritto;
  2. impatto su data release;
  3. criteri di accettazione aggiunti/aggiornati.
- Ogni modifica approvata deve essere registrata nella tabella sotto.

| Data       | Proposta                    | Decisione | Impatto         | Owner |
|------------|-----------------------------|-----------|-----------------|-------|
| 2026-02-24 | Scope freeze iniziale 3.4.0 | Approvata | Scope baseline  | Team  |

## 8) Documenti correlati

- `docs/implementation_roadmap.md`
- `docs/release_process.md`
- `docs/release_compliance_checklist.md`
- `docs/release_notes_template.md`
