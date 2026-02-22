# DEV Profiling Guide

This mode runs AiringDeck in a development context with Python profiling enabled.

## Quick command

```bash
python scripts/profile_dev.py --duration-ms 15000 --top 40
```

## What it does

1. Starts the app with `cProfile`.
2. Sets environment variables:
   - `AIRINGDECK_PROFILE=1`
   - `AIRINGDECK_AUTO_EXIT_MS=<duration>`
3. Automatically closes the app after the configured duration.
4. Writes outputs into `profiles/`:
   - raw `.prof` file
   - top cumulative report
   - top self-time report
   - stdout/stderr log

## Notes

- This profiling mode mainly measures Python-side execution.
- For QML/scene graph profiling, also use Qt Creator QML Performance Monitor.
