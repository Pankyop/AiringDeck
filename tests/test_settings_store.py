import sqlite3

from core.settings_store import (
    SCHEMA_VERSION,
    SQLiteSettingsStore,
    _coerce_expected,
    _coerce_requested,
    _parse_bool,
    _resolve_default_db_path,
    open_settings_store,
)


class LegacySettings:
    def __init__(self, initial_store=None):
        self._store = dict(initial_store or {})

    def value(self, key, default=None, type=None):  # noqa: A002
        value = self._store.get(key, default)
        if type is None or value is None:
            return value
        try:
            return type(value)
        except Exception:
            return default

    def setValue(self, key, value):
        self._store[key] = value

    def remove(self, key):
        self._store.pop(key, None)


def test_sqlite_migration_first_run_copies_legacy_values(tmp_path):
    db_path = tmp_path / "settings.sqlite3"
    legacy = LegacySettings(
        {
            "app_language": "en",
            "min_score": "44",
            "update_checks_enabled": "false",
            "notification_lead_minutes": "30",
        }
    )

    store = open_settings_store(legacy, db_path=db_path)

    assert store.value("app_language", "it", type=str) == "en"
    assert store.value("min_score", 0, type=int) == 44
    assert store.value("update_checks_enabled", True, type=bool) is False
    assert store.value("notification_lead_minutes", 15, type=int) == 30

    conn = sqlite3.connect(db_path)
    try:
        schema = conn.execute(
            "SELECT value FROM app_metadata WHERE key = 'schema_version'"
        ).fetchone()
    finally:
        conn.close()
    assert schema is not None
    assert int(schema[0]) == SCHEMA_VERSION


def test_sqlite_migration_is_idempotent_on_restart(tmp_path):
    db_path = tmp_path / "settings.sqlite3"

    store_first = open_settings_store(
        LegacySettings({"app_language": "en"}),
        db_path=db_path,
    )
    store_first.setValue("app_language", "it")

    store_second = open_settings_store(
        LegacySettings({"app_language": "en"}),
        db_path=db_path,
    )

    assert store_second.value("app_language", "en", type=str) == "it"


def test_open_settings_store_falls_back_to_legacy_on_sqlite_error(monkeypatch, tmp_path):
    legacy = LegacySettings({"app_language": "en"})

    def _boom(*_args, **_kwargs):
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr("core.settings_store.sqlite3.connect", _boom)

    store = open_settings_store(legacy, db_path=tmp_path / "settings.sqlite3")

    assert store is legacy
    store.setValue("only_today", True)
    assert legacy._store["only_today"] is True


def test_coerce_helpers_handle_edge_cases():
    assert _parse_bool(True) is True
    assert _parse_bool(0) is False
    assert _parse_bool(1.0) is True
    assert _parse_bool(" yes ") is True
    assert _parse_bool("off") is False
    assert _parse_bool("invalid", default=True) is True

    assert _coerce_expected("42", int) == 42
    assert _coerce_expected("bad", int) is None
    assert _coerce_expected("true", bool) is True
    assert _coerce_expected("?", bool) is None
    assert _coerce_expected(123, str) == "123"
    assert _coerce_expected("abc", None) == "abc"

    assert _coerce_requested("1", False, bool) is True
    assert _coerce_requested("bad", True, bool) is True
    assert _coerce_requested("19", 0, int) == 19
    assert _coerce_requested("bad", 5, int) == 5
    assert _coerce_requested(None, "fallback", str) is None
    assert _coerce_requested("raw", "fallback", None) == "raw"


def test_resolve_default_db_path_prefers_env(monkeypatch):
    monkeypatch.setenv("AIRINGDECK_SETTINGS_DB_PATH", "C:/tmp/airingdeck-test.sqlite3")

    assert _resolve_default_db_path(LegacySettings()) == "C:/tmp/airingdeck-test.sqlite3"


def test_resolve_default_db_path_uses_memory_for_non_qt_legacy(monkeypatch):
    monkeypatch.delenv("AIRINGDECK_SETTINGS_DB_PATH", raising=False)

    assert _resolve_default_db_path(LegacySettings()) == ":memory:"


def test_resolve_default_db_path_fallback_when_qt_standard_paths_fail(monkeypatch):
    monkeypatch.delenv("AIRINGDECK_SETTINGS_DB_PATH", raising=False)

    class _QtLegacy:
        __module__ = "PySide6.QtCore"

    import builtins

    real_import = builtins.__import__

    def _failing_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "PySide6.QtCore":
            raise RuntimeError("qt paths unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _failing_import)

    path = _resolve_default_db_path(_QtLegacy())

    assert path.endswith("settings_v1.sqlite3")


def test_sqlite_remove_falls_back_to_null_write_when_legacy_remove_fails(tmp_path):
    class FailingRemoveLegacy(LegacySettings):
        def __init__(self):
            super().__init__()
            self.set_calls = []

        def remove(self, key):
            raise RuntimeError("remove failed")

        def setValue(self, key, value):
            self.set_calls.append((key, value))
            super().setValue(key, value)

    legacy = FailingRemoveLegacy()
    store = open_settings_store(legacy, db_path=tmp_path / "settings.sqlite3")

    store.setValue("selected_genre", "Action")
    store.setValue("selected_genre", None)

    assert store.value("selected_genre", "All genres", type=str) == "All genres"
    assert ("selected_genre", None) in legacy.set_calls


def test_sqlite_store_without_legacy_remove_and_close_paths():
    store = SQLiteSettingsStore(":memory:", legacy_settings=None)

    store.setValue("sort_field", "score")
    store.remove("sort_field")

    assert store.value("sort_field", "airing_time", type=str) == "airing_time"
    store.close()


def test_decode_invalid_numeric_values_return_none(tmp_path):
    store = open_settings_store(LegacySettings(), db_path=tmp_path / "settings.sqlite3")
    store.setValue("numeric_test", 1)

    with store._conn:
        store._conn.execute(
            "UPDATE app_settings SET value_type = ?, value_text = ? WHERE key = ?",
            ("int", "not-a-number", "numeric_test"),
        )
    assert store.value("numeric_test", 0, type=int) is None

    with store._conn:
        store._conn.execute(
            "UPDATE app_settings SET value_type = ?, value_text = ? WHERE key = ?",
            ("float", "still-bad", "numeric_test"),
        )
    assert store.value("numeric_test", 0.0, type=float) is None
