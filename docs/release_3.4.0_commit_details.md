# Release 3.4.0 - Commit Details

Release tag: `v3.4.0`  
Primary release commit: `6985d4b` (`chore(release): 3.4.0`)

## Included files

- `CHANGELOG.md`
- `README.md`
- `VERSIONE.md`
- `docs/release_notes_3.4.0.md`
- `docs/release_scope_3.4.0.it.md`
- `docs/release_scope_3.4.0.md`
- `docs/test_report_full.md`
- `pyproject.toml`
- `setup.py`
- `src/core/app_controller.py`
- `src/services/update_service.py`
- `src/ui/qml/MainContent.qml`
- `src/ui/qml/components/Settings/SettingsDialog.qml`
- `src/version.py`
- `tests/test_anilist_service.py`
- `tests/test_auth_service.py`
- `tests/test_concurrency_controller.py`
- `tests/test_integration_controller_flow.py`
- `tests/test_main_bootstrap.py`
- `tests/test_no_tracker_mode.py`
- `tests/test_ui_localization.py`
- `tests/test_update_service.py`
- `tests/test_worker.py`

## Functional areas covered

- Horizontal redesign of Settings UI.
- Removal of background sync config from Settings.
- Manual "Check now" update action in Settings.
- In-app updater flow (download and direct installer launch).
- Update modal text/behavior alignment for direct install.
- Version bump to `3.4.0` across runtime and packaging metadata.
- Test suite expansion and update-flow validation.
