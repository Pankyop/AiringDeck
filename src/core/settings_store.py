import logging
import os
import sqlite3
from pathlib import Path
from typing import Any


logger = logging.getLogger("airingdeck.settings")

SCHEMA_VERSION = 1
_SCHEMA_VERSION_KEY = "schema_version"
_LEGACY_MIGRATION_KEY = "legacy_qsettings_migration_v1"

_SETTINGS_TYPE_HINTS: dict[str, type] = {
    "use_english_title": bool,
    "selected_genre": str,
    "only_today": bool,
    "min_score": int,
    "sort_field": str,
    "sort_ascending": bool,
    "app_language": str,
    "notifications_enabled": bool,
    "notification_lead_minutes": int,
    "dismissed_update_version": str,
    "update_checks_enabled": bool,
    "diagnostics_enabled": bool,
    "privacy_notice_seen": bool,
    "cached_user_info": str,
    "cached_anime_list": str,
}


def _parse_bool(value: Any, default: bool | None = None) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
    return default


def _coerce_expected(value: Any, expected: type | None) -> Any:
    if expected is None:
        return value
    if expected is bool:
        return _parse_bool(value, None)
    if expected is int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    if expected is str:
        return str(value)
    try:
        return expected(value)
    except Exception:
        return None


def _coerce_requested(value: Any, default: Any, requested_type: type | None) -> Any:
    if requested_type is None:
        return value
    if value is None:
        return value
    if requested_type is bool:
        coerced = _parse_bool(value, None)
        return default if coerced is None else coerced
    try:
        return requested_type(value)
    except Exception:
        return default


def _resolve_default_db_path(legacy_settings: Any | None) -> str:
    env_path = os.getenv("AIRINGDECK_SETTINGS_DB_PATH", "").strip()
    if env_path:
        return env_path

    module_name = getattr(getattr(legacy_settings, "__class__", object), "__module__", "")
    if module_name and not module_name.startswith("PySide6"):
        return ":memory:"

    try:
        from PySide6.QtCore import QStandardPaths

        config_dir = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
    except Exception:
        config_dir = ""
    if config_dir:
        return str(Path(config_dir) / "settings_v1.sqlite3")
    return str(Path.home() / ".airingdeck" / "settings_v1.sqlite3")


class SQLiteSettingsStore:
    def __init__(self, db_path: str | Path, legacy_settings: Any | None = None):
        self._legacy_settings = legacy_settings
        self._db_path = str(db_path)
        if self._db_path != ":memory:":
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._db_path)
        self._bootstrap()
        self._migrate_legacy_once()

    def close(self):
        self._conn.close()

    def _bootstrap(self):
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS app_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value_type TEXT NOT NULL,
                    value_text TEXT
                )
                """
            )
            if self._meta_get(_SCHEMA_VERSION_KEY) is None:
                self._meta_set(_SCHEMA_VERSION_KEY, str(SCHEMA_VERSION))

    def _meta_get(self, key: str) -> str | None:
        row = self._conn.execute(
            "SELECT value FROM app_metadata WHERE key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return None
        return str(row[0])

    def _meta_set(self, key: str, value: str):
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO app_metadata(key, value)
                VALUES(?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    def _migrate_legacy_once(self):
        if self._meta_get(_LEGACY_MIGRATION_KEY) == "1":
            return

        if self._legacy_settings is not None:
            for key, expected_type in _SETTINGS_TYPE_HINTS.items():
                try:
                    legacy_value = self._legacy_settings.value(key)
                except Exception as exc:
                    logger.warning("Skipping legacy key '%s' during migration: %s", key, exc)
                    continue
                if legacy_value is None:
                    continue
                normalized = _coerce_expected(legacy_value, expected_type)
                if normalized is None:
                    continue
                self._set_sql_value(key, normalized, overwrite=False)

        self._meta_set(_LEGACY_MIGRATION_KEY, "1")

    @staticmethod
    def _encode(value: Any) -> tuple[str, str]:
        if isinstance(value, bool):
            return "bool", "1" if value else "0"
        if isinstance(value, int) and not isinstance(value, bool):
            return "int", str(value)
        if isinstance(value, float):
            return "float", repr(value)
        return "str", str(value)

    @staticmethod
    def _decode(value_type: str, value_text: str | None) -> Any:
        raw = value_text if value_text is not None else ""
        if value_type == "bool":
            return raw == "1"
        if value_type == "int":
            try:
                return int(raw)
            except (TypeError, ValueError):
                return None
        if value_type == "float":
            try:
                return float(raw)
            except (TypeError, ValueError):
                return None
        return raw

    def _set_sql_value(self, key: str, value: Any, overwrite: bool):
        value_type, value_text = self._encode(value)
        with self._conn:
            if overwrite:
                self._conn.execute(
                    """
                    INSERT INTO app_settings(key, value_type, value_text)
                    VALUES(?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        value_type = excluded.value_type,
                        value_text = excluded.value_text
                    """,
                    (key, value_type, value_text),
                )
                return
            self._conn.execute(
                """
                INSERT OR IGNORE INTO app_settings(key, value_type, value_text)
                VALUES(?, ?, ?)
                """,
                (key, value_type, value_text),
            )

    def value(self, key: str, default: Any = None, type: type | None = None):  # noqa: A002
        row = self._conn.execute(
            "SELECT value_type, value_text FROM app_settings WHERE key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return default
        decoded = self._decode(str(row[0]), row[1])
        return _coerce_requested(decoded, default, type)

    def setValue(self, key: str, value: Any):
        if value is None:
            self.remove(key)
            return
        self._set_sql_value(key, value, overwrite=True)
        if self._legacy_settings is not None:
            try:
                self._legacy_settings.setValue(key, value)
            except Exception:
                logger.debug("Legacy mirror write failed for key '%s'", key, exc_info=True)

    def remove(self, key: str):
        with self._conn:
            self._conn.execute("DELETE FROM app_settings WHERE key = ?", (key,))
        if self._legacy_settings is None:
            return
        remove_fn = getattr(self._legacy_settings, "remove", None)
        if callable(remove_fn):
            try:
                remove_fn(key)
                return
            except Exception:
                logger.debug("Legacy remove failed for key '%s'", key, exc_info=True)
        try:
            self._legacy_settings.setValue(key, None)
        except Exception:
            logger.debug("Legacy null-write failed for key '%s'", key, exc_info=True)


def open_settings_store(legacy_settings: Any, db_path: str | Path | None = None):
    target_path = str(db_path) if db_path is not None else _resolve_default_db_path(legacy_settings)
    try:
        return SQLiteSettingsStore(target_path, legacy_settings=legacy_settings)
    except Exception as exc:
        logger.warning("SQLite settings unavailable, using QSettings fallback: %s", exc)
        return legacy_settings

