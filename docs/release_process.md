# AiringDeck - Processo Release e Tag

Ultimo aggiornamento: 2026-02-19

## 1) Scope

Questo documento definisce il processo minimo per pubblicare release coerenti
con SemVer e prerelease (`-beta`, `-rc`).

## 2) Prerequisiti

- Branch aggiornato e sincronizzato con `origin/master`.
- Pipeline CI verde.
- Working tree pulito (`git status` senza modifiche da committare).

## 3) Checklist pre-release

1. Allineare versione in:
`src/version.py`, `pyproject.toml`, `setup.py`.

2. Eseguire quality gate:
`python scripts/run_quality_suite.py`.

3. Eseguire check runtime smoke:
`AIRINGDECK_AUTO_EXIT_MS=12000 python src/main.py`.

4. Aggiornare `CHANGELOG.md`:
- spostare voci da `Unreleased` alla nuova versione.
- aggiungere data release (`YYYY-MM-DD`).

5. Generare installer Windows:
`python scripts/build_windows_installer.py --skip-build-exe`
  (oppure senza `--skip-build-exe` per rifare anche la build app).

## 4) Commit release

Esempio commit:

```bash
git add src/version.py pyproject.toml setup.py CHANGELOG.md
git commit -m "chore(release): 3.3.0"
```

## 5) Creazione tag

Usare sempre tag annotati:

```bash
git tag -a v3.3.0 -m "AiringDeck 3.3.0"
```

Pubblicazione:

```bash
git push origin master
git push origin v3.3.0
```

## 6) Regole incremento versione

- `PATCH` (`X.Y.Z`): bugfix/hardening senza breaking changes.
- `MINOR` (`X.Y+1.0`): feature backward-compatible.
- `MAJOR` (`X+1.0.0`): breaking changes.
- Prerelease:
- `X.Y.Z-beta.N` durante validazione funzionale.
- `X.Y.Z-rc.N` in freeze pre-stable.

## 7) Definition of Done release

- CI verde.
- Changelog aggiornato.
- Tag pubblicato.
- Build smoke riuscita.
- Installer Windows generato (`dist/AiringDeck-Setup-<version>.exe`).
- Nessun blocco P0 aperto in roadmap.
