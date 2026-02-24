# Release v3.4.0

Release date: 2026-02-24

## Highlights

- Nuovo menu Impostazioni con layout orizzontale e struttura piu chiara.
- Rimosso il sync in background periodico dalle impostazioni.
- Nuovo pulsante `Controlla ora` per verifica aggiornamenti on-demand.
- Nuovo updater in-app: `Aggiorna ora` scarica e avvia direttamente l'installer Windows.

## Fixes

- Pulsante e testo di notifica test visibili solo in profilo dev/test.
- Migliorata la coerenza di accessibilita e navigazione tastiera nel flusso update/settings.

## Performance

- Nessun cambiamento regressivo atteso nel runtime; refresh UI settings senza impatti sul calendario.

## Compliance (required)

### Data & Privacy impact

- Nessuna nuova telemetria remota introdotta.
- Download update attivato solo su azione esplicita dell'utente.

### Network/API impact

- Update check resta su GitHub Releases/Tags.
- In presenza di asset release Windows, l'app usa direttamente l'installer come payload update.

### AniList usage statement

- AiringDeck uses AniList OAuth + GraphQL under AniList terms.
- No-Tracker mode remains active (local viewer model, no AiringDeck cloud tracker backend).

## Upgrade notes

- Gli utenti da versioni precedenti possono aggiornare da avviso in-app.
- Se una release non espone un installer Windows tra gli asset, l'update diretto non viene avviato.
