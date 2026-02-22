# AiringDeck - Release and Tag Process

Last updated: 2026-02-22

## 1) Scope

This document defines the minimum process to publish releases aligned with
SemVer and prerelease identifiers (`-beta`, `-rc`).

## 2) Prerequisites

- Branch updated and synced with `origin/master`.
- CI pipeline green.
- Clean working tree (`git status` with nothing to commit).

## 3) Pre-release checklist

1. Align version in:
`src/version.py`, `pyproject.toml`, `setup.py`.

2. Run quality gates:
`python scripts/run_quality_suite.py`.

3. Run runtime smoke check:
`AIRINGDECK_AUTO_EXIT_MS=12000 python src/main.py`.

4. Update `CHANGELOG.md`:
- move entries from `Unreleased` into the new version section,
- add release date (`YYYY-MM-DD`).

5. Generate Windows installer:
`python scripts/build_windows_installer.py --skip-build-exe`
  (or omit `--skip-build-exe` to rebuild the app first).

## 4) Release commit

Example:

```bash
git add src/version.py pyproject.toml setup.py CHANGELOG.md
git commit -m "chore(release): 3.3.0"
```

## 5) Tag creation

Always use annotated tags:

```bash
git tag -a v3.3.0 -m "AiringDeck 3.3.0"
```

Publish:

```bash
git push origin master
git push origin v3.3.0
```

## 6) Version increment rules

- `PATCH` (`X.Y.Z`): bugfix/hardening without breaking changes.
- `MINOR` (`X.Y+1.0`): backward-compatible features.
- `MAJOR` (`X+1.0.0`): breaking changes.
- Prerelease:
- `X.Y.Z-beta.N` during functional validation.
- `X.Y.Z-rc.N` during pre-stable freeze.

## 7) Release Definition of Done

- CI green.
- Changelog updated.
- Tag published.
- Build smoke successful.
- Windows installer generated (`dist/AiringDeck-Setup-<version>.exe`).
- No open P0 blockers in roadmap.

## 8) Automated X release post

The repository includes `.github/workflows/x_release.yml`, which triggers on:
- GitHub release publication (`release.published`)
- manual dispatch (`workflow_dispatch`)

It runs `scripts/post_to_x.py` and publishes a release thread from
`CHANGELOG.md`.

Required repository secrets:
- `X_POST_ENABLED` = `true` (if missing/false, script runs in dry-run)
- `X_API_KEY`
- `X_API_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`

Optional:
- `X_BEARER_TOKEN` (used only if OAuth1 credentials are not provided)

Manual verification (no posting):

```bash
python scripts/post_to_x.py --tag v3.3.0 --dry-run
```
