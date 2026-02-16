# DEV Profiling Guide

Questa modalita esegue AiringDeck in contesto development con profiling Python attivo.

## Comando rapido

```bash
python scripts/profile_dev.py --duration-ms 15000 --top 40
```

## Cosa fa

1. Avvia l'app con `cProfile`.
2. Imposta variabili ambiente:
   - `AIRINGDECK_PROFILE=1`
   - `AIRINGDECK_AUTO_EXIT_MS=<durata>`
3. Chiude automaticamente l'app dopo la durata specificata.
4. Salva in `profiles/`:
   - file raw `.prof`
   - report top cumulative
   - report top self-time
   - log stdout/stderr

## Note

- Questo profiling misura soprattutto il lato Python.
- Per profiling QML/scene graph usare anche Qt Creator QML Performance Monitor.
