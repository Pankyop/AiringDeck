from PySide6.QtCore import QObject, Signal

import core.app_controller as app_controller_module


class _FakeSettings:
    _store = {}

    def __init__(self, org, app):
        self._org = org
        self._app = app

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


class _FakeThreadPool:
    def __init__(self):
        self.started = 0

    def maxThreadCount(self):
        return 1

    def start(self, worker):
        self.started += 1
        worker.run()


class _FakeAuthService(QObject):
    auth_completed = Signal(str)
    auth_failed = Signal(str)

    def __init__(self):
        super().__init__()
        self._saved_token = ""

    def get_saved_token(self):
        return self._saved_token

    def clear_token(self):
        self._saved_token = ""

    def start_auth_flow(self):
        return None


class _FakeAniListService:
    def __init__(self):
        self.token = None

    def set_token(self, token):
        self.token = token

    def get_viewer_info(self):
        return {
            "id": 7,
            "name": "tester",
            "avatar": {"large": "https://example/avatar.png"},
        }

    def get_watching_anime(self, user_id):
        return []


class _FakeUpdateService:
    def __init__(self):
        self.feed_url = "https://example.test/releases/latest"
        self.tags_url = "https://example.test/tags"
        self.calls = 0

    def check_latest(self, current_version):
        self.calls += 1
        return {"available": False, "current_version": current_version}


def _make_controller(monkeypatch, initial_store=None):
    _FakeSettings._store = dict(initial_store or {})
    monkeypatch.setattr(app_controller_module, "QSettings", _FakeSettings)
    monkeypatch.setattr(app_controller_module, "QThreadPool", _FakeThreadPool)
    monkeypatch.setattr(app_controller_module, "AuthService", _FakeAuthService)
    monkeypatch.setattr(app_controller_module, "AniListService", _FakeAniListService)
    monkeypatch.setattr(app_controller_module, "UpdateService", _FakeUpdateService)
    monkeypatch.setattr(app_controller_module.AppController, "_init_tray_icon", lambda self: None)
    controller = app_controller_module.AppController(None)
    controller._update_timer.stop()
    controller._filter_update_timer.stop()
    controller._sync_retry_timer.stop()
    return controller


def test_no_tracker_defaults_require_privacy_ack(monkeypatch):
    c = _make_controller(monkeypatch)

    assert c.noTrackerMode is True
    assert c.showPrivacyNotice is True
    assert c.updateChecksEnabled is True
    assert c.diagnosticsEnabled is False


def test_initialize_skips_network_until_privacy_is_accepted(monkeypatch):
    c = _make_controller(monkeypatch)
    calls = {"updates": 0}

    monkeypatch.setattr(c, "checkForUpdates", lambda: calls.__setitem__("updates", calls["updates"] + 1))
    c.initialize()

    assert calls["updates"] == 0
    assert "privacy" in c.statusMessage.lower()


def test_apply_privacy_preferences_persists_and_bootstraps(monkeypatch):
    c = _make_controller(monkeypatch)
    calls = {"updates": 0}

    monkeypatch.setattr(c, "checkForUpdates", lambda: calls.__setitem__("updates", calls["updates"] + 1))
    c.applyPrivacyPreferences(True, True, True)

    assert c.showPrivacyNotice is False
    assert c.notificationsEnabled is True
    assert c.updateChecksEnabled is True
    assert c.diagnosticsEnabled is True
    assert _FakeSettings._store["privacy_notice_seen"] is True
    assert _FakeSettings._store.get("update_checks_enabled", True) is True
    assert _FakeSettings._store["diagnostics_enabled"] is True
    assert calls["updates"] == 1


def test_check_for_updates_respects_disabled_setting(monkeypatch):
    c = _make_controller(monkeypatch, initial_store={"privacy_notice_seen": True, "update_checks_enabled": False})
    c.updateChecksEnabled = False
    c._thread_pool.started = 0

    c.checkForUpdates()

    assert c._thread_pool.started == 0


def test_open_selected_anime_on_anilist_uses_site_url(monkeypatch):
    c = _make_controller(monkeypatch)
    c._selected_anime = {"media": {"siteUrl": "https://anilist.co/anime/123"}}
    opened = {"url": None}

    def _fake_open(url):
        opened["url"] = url.toString()
        return True

    monkeypatch.setattr(app_controller_module.QDesktopServices, "openUrl", _fake_open)
    c.openSelectedAnimeOnAniList()

    assert opened["url"] == "https://anilist.co/anime/123"
