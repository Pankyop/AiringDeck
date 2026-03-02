import sqlite3

from core.settings_store import SCHEMA_VERSION, open_settings_store


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

