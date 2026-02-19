# Manual Checklist - Multi-Monitor and DPI

Ultimo aggiornamento: 2026-02-19

## 1) Scopo

Ridurre regressioni visuali su layout QML (testi tagliati, overlap, elementi fuori viewport)
in scenari reali con monitor multipli e scaling diversi.

## 2) Setup minimo

- OS: Windows 10/11.
- Display A: schermo laptop (es. 125%).
- Display B: monitor esterno/TV (es. 100%).
- App in build corrente (`dist/AiringDeck.exe`) e in run Python (`python src/main.py`).

## 3) Matrice test obbligatoria

- Risoluzioni:
  - 1920x1080
  - 2560x1440 (se disponibile)
- Scaling:
  - 100%
  - 125%
  - 150%
- Modalita:
  - finestra normale
  - massimizzata
  - fullscreen (quando applicabile)
- Posizionamento:
  - avvio su monitor principale
  - trascinamento e uso completo su monitor secondario

## 4) Checklist UI da validare

### Header + filtri

- Il campo ricerca non si sovrappone ai controlli a destra.
- Combo genere/sort mostrano testo leggibile e non tagliato.
- Pulsanti `ASC/DESC` e `Reset` sempre visibili.
- Checkbox `Solo oggi` leggibile su tutti gli scaling.

### Calendario e card

- Titoli card lunghi su piu righe senza taglio orizzontale.
- Badge episodio (`Ep.`) sempre dentro card.
- Nessun overlap tra card in `Flow` durante resize.

### Sidebar dettagli

- Cover principale sempre visibile (o fallback testuale).
- Titolo anime lungo non deve essere tagliato sul bordo destro.
- Campi `Progresso/Prossimo` allineati e leggibili.

### Dialog e impostazioni

- About e Settings centrati e completamente visibili.
- Pulsanti di chiusura accessibili da tastiera (`Tab`, `Enter`).
- Cambio lingua non rompe layout (IT/EN).

## 5) Checklist accessibilita tastiera

- Tab order continuo:
  - ricerca -> sync -> profilo/login -> filtri -> sort -> reset.
- `Enter`/`Space` funzionano su:
  - sync
  - login/profilo
  - card anime selezionabili
- Focus visivo percepibile sugli elementi interattivi.

## 6) Criteri di accettazione

- Nessun testo critico tagliato.
- Nessun controllo essenziale non raggiungibile.
- Nessun overlap bloccante in header/filtri/sidebar.
- Nessun crash/freeze durante resize, cambio monitor, cambio scaling.

## 7) Evidenze da allegare

- Screenshot:
  - `resources/images/qa/dpi_100_main.png`
  - `resources/images/qa/dpi_125_main.png`
  - `resources/images/qa/dpi_150_secondary.png`
- Nota breve per ogni eventuale anomalia con:
  - monitor/scaling
  - sezione UI
  - comportamento osservato
