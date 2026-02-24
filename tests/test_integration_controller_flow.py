from datetime import datetime, timedelta

from PySide6.QtCore import QObject, Signal

import core.app_controller as app_controller_module


class FakeSettings:
    _store = {}

    def __init__(self, org, app):
        self._org = org
        self._app = app

    def value(self, key, default=None, type=None):  # noqa: A002
        val = self._store.get(key, default)
        if type is None or val is None:
            return val
        try:
            return type(val)
        except Exception:
            return default

    def setValue(self, key, value):
        self._store[key] = value


class FakeThreadPool:
    def __init__(self):
        self.started = 0

    def maxThreadCount(self):
        return 1

    def start(self, worker):
        self.started += 1
        worker.run()


class FakeAuthService(QObject):
    auth_completed = Signal(str)
    auth_failed = Signal(str)

    def __init__(self):
        super().__init__()
        self.cleared = False

    def get_saved_token(self):
        return None

    def clear_token(self):
        self.cleared = True

    def start_auth_flow(self):
        return None


class FakeAniListService:
    def __init__(self):
        self.token = None

    def set_token(self, token):
        self.token = token

    def get_viewer_info(self):
        return {
            "id": 77,
            "name": "ketou",
            "avatar": {"large": "https://example.com/avatar.png"},
        }

    def get_watching_anime(self, user_id):
        now = datetime.now()
        return [
            {
                "media": {
                    "id": 1,
                    "title": {"romaji": "One Piece", "english": "One Piece"},
                    "genres": ["Action"],
                    "averageScore": 80,
                    "nextAiringEpisode": {
                        "episode": 1102,
                        "airingAt": int((now + timedelta(hours=2)).timestamp()),
                        "timeUntilAiring": 0,
                    },
                    "coverImage": {"large": "", "medium": ""},
                },
                "progress": 1101,
            },
            {
                "media": {
                    "id": 2,
                    "title": {"romaji": "Oshi no Ko", "english": "Oshi no Ko"},
                    "genres": ["Drama"],
                    "averageScore": 92,
                    "nextAiringEpisode": {
                        "episode": 5,
                        "airingAt": int((now + timedelta(hours=1)).timestamp()),
                        "timeUntilAiring": 0,
                    },
                    "coverImage": {"large": "", "medium": ""},
                },
                "progress": 4,
            },
        ]


class FakeUpdateService:
    def check_latest(self, current_version):
        return {
            "available": True,
            "current_version": current_version,
            "latest_version": "3.4.0",
            "title": "3.4.0",
            "notes": "• Better notifications\n• Faster startup",
            "download_url": "https://example.com/releases/3.4.0",
            "published_at": "2026-02-19T12:00:00Z",
            "source": "release",
        }


class FakeNoUpdateService:
    def check_latest(self, current_version):
        return {
            "available": False,
            "current_version": current_version,
            "latest_version": current_version,
        }


class FlakyAniListService(FakeAniListService):
    def __init__(self):
        super().__init__()
        self._watching_calls = 0

    def get_watching_anime(self, user_id):
        self._watching_calls += 1
        if self._watching_calls == 1:
            raise Exception("ConnectionError: Unable to reach AniList")
        return super().get_watching_anime(user_id)


class TwoFailureAniListService(FakeAniListService):
    def __init__(self):
        super().__init__()
        self._watching_calls = 0

    def get_watching_anime(self, user_id):
        self._watching_calls += 1
        if self._watching_calls <= 2:
            raise Exception("ConnectionError: Unable to reach AniList")
        return super().get_watching_anime(user_id)


def _make_controller(
    monkeypatch,
    service_cls=FakeAniListService,
    update_service_cls=FakeUpdateService,
    initial_store=None,
):
    FakeSettings._store = dict(initial_store or {})
    monkeypatch.setattr(app_controller_module, "QSettings", FakeSettings)
    monkeypatch.setattr(app_controller_module, "QThreadPool", FakeThreadPool)
    monkeypatch.setattr(app_controller_module, "AuthService", FakeAuthService)
    monkeypatch.setattr(app_controller_module, "AniListService", service_cls)
    monkeypatch.setattr(app_controller_module, "UpdateService", update_service_cls)
    monkeypatch.setattr(app_controller_module.AppController, "_init_tray_icon", lambda self: None)

    c = app_controller_module.AppController(None)
    c._update_timer.stop()
    c._filter_update_timer.stop()
    c._sync_retry_timer.stop()
    return c


def test_integration_auth_to_sync_populates_models(monkeypatch):
    c = _make_controller(monkeypatch)

    c._on_auth_completed("token-123")

    assert c.isAuthenticated is True
    assert c.userInfo["name"] == "ketou"
    assert c.allAnimeModel.rowCount() == 2
    assert c.dailyCounts == [len(c.dayModels[i]._entries) for i in range(7)]
    assert "Sincronizzati 2 anime" in c.statusMessage


def test_integration_filters_and_sort_update_output(monkeypatch):
    c = _make_controller(monkeypatch)
    c._on_auth_completed("token-123")

    c.selectedGenre = "Drama"
    c.minScore = 90
    c.sortField = "score"
    c.sortAscending = False

    c.setFilterText("oshi")
    c._apply_pending_filter()

    assert c.allAnimeModel.rowCount() == 1
    assert c.allAnimeModel.get_entry(0)["media"]["id"] == 2


def test_integration_http401_error_triggers_logout(monkeypatch):
    c = _make_controller(monkeypatch)
    c._on_auth_completed("token-123")
    assert c.isAuthenticated is True
    assert c.allAnimeModel.rowCount() > 0

    c._on_error((Exception, Exception("HTTP401: Not authenticated"), "trace"))

    assert c.isAuthenticated is False
    assert c.allAnimeModel.rowCount() == 0
    assert c._full_anime_list == []
    assert c._full_airing_entries == []
    assert c.userInfo == {}
    assert "Disconnesso" in c.statusMessage


def test_integration_connection_error_message_without_logout(monkeypatch):
    c = _make_controller(monkeypatch)
    c._on_auth_completed("token-123")
    assert c.isAuthenticated is True

    c._on_error((Exception, Exception("ConnectionError: Unable to reach AniList"), "trace"))

    assert c.isAuthenticated is True
    assert "Rete non disponibile" in c.statusMessage


def test_integration_unknown_error_maps_to_generic_message(monkeypatch):
    c = _make_controller(monkeypatch)
    c._on_auth_completed("token-123")
    assert c.isAuthenticated is True

    c._on_error((Exception, Exception("Totally unexpected"), "trace"))

    assert c.isAuthenticated is True
    assert "Errore imprevisto" in c.statusMessage


def test_integration_timeout_error_message_without_logout(monkeypatch):
    c = _make_controller(monkeypatch)
    c._on_auth_completed("token-123")
    assert c.isAuthenticated is True

    c._on_error((Exception, Exception("Timeout: AniList request timed out"), "trace"))

    assert c.isAuthenticated is True
    assert "Timeout della richiesta" in c.statusMessage


def test_integration_rate_limit_error_message_without_logout(monkeypatch):
    c = _make_controller(monkeypatch)
    c._on_auth_completed("token-123")
    assert c.isAuthenticated is True

    c._on_error((Exception, Exception("HTTP429: Rate limit exceeded"), "trace"))

    assert c.isAuthenticated is True
    assert "Limite AniList raggiunto" in c.statusMessage


def test_integration_recovers_after_transient_sync_error(monkeypatch):
    c = _make_controller(monkeypatch, service_cls=FlakyAniListService)

    c._on_auth_completed("token-123")
    c._on_sync_retry_timeout()
    assert c.isAuthenticated is True
    assert c.isAuthenticated is True
    assert c.allAnimeModel.rowCount() == 2
    assert "Sincronizzati 2 anime" in c.statusMessage


def test_integration_sync_transient_error_exhausts_auto_retry_then_manual_recovery(monkeypatch):
    c = _make_controller(monkeypatch, service_cls=TwoFailureAniListService)

    c._on_auth_completed("token-123")
    c._on_sync_retry_timeout()
    assert c.isAuthenticated is True
    assert "Rete non disponibile" in c.statusMessage

    c.syncAnimeList()

    assert c.allAnimeModel.rowCount() == 2
    assert "Sincronizzati 2 anime" in c.statusMessage


def test_integration_sync_without_auth_sets_explicit_message(monkeypatch):
    c = _make_controller(monkeypatch)

    c.syncAnimeList()

    assert "Effettua il login" in c.statusMessage


def test_integration_sync_with_missing_user_id_sets_profile_message(monkeypatch):
    c = _make_controller(monkeypatch)
    c._is_authenticated = True
    c._user_info = {"name": "ketou"}

    c.syncAnimeList()

    assert "Profilo non pronto" in c.statusMessage


def test_integration_adaptive_sync_backoff_is_bounded_and_deterministic(monkeypatch):
    c = _make_controller(monkeypatch)

    timeout_delay = c._compute_sync_retry_delay_ms(1, "timeout")
    rate_limit_delay = c._compute_sync_retry_delay_ms(1, "http429: rate limit exceeded")
    doubled_timeout_delay = c._compute_sync_retry_delay_ms(2, "timeout")
    capped_delay = c._compute_sync_retry_delay_ms(8, "http429: rate limit exceeded")

    assert timeout_delay == 4000
    assert rate_limit_delay == 10000
    assert doubled_timeout_delay == 8000
    assert capped_delay == c.MAX_SYNC_RETRY_DELAY_MS


def test_integration_update_check_sets_banner_state(monkeypatch):
    c = _make_controller(monkeypatch)

    c.checkForUpdates()

    assert c.updateAvailable is True
    assert c.updateLatestVersion == "3.4.0"
    assert "Better notifications" in c.updateNotes
    assert c.updateDownloadUrl == "https://example.com/releases/3.4.0"


def test_integration_update_dismiss_persists_version(monkeypatch):
    c = _make_controller(monkeypatch)
    c.checkForUpdates()
    assert c.updateAvailable is True

    c.dismissUpdateNotice()

    assert c.updateAvailable is False
    assert FakeSettings._store.get("dismissed_update_version") == "3.4.0"


def test_integration_dismissed_update_version_stays_hidden(monkeypatch):
    c = _make_controller(monkeypatch, initial_store={"dismissed_update_version": "3.4.0"})

    c.checkForUpdates()

    assert c.updateAvailable is False


def test_integration_start_update_install(monkeypatch):
    c = _make_controller(monkeypatch)
    c.checkForUpdates()
    launched = {"path": None}

    class _FakeApp:
        def __init__(self):
            self.quit_calls = 0

        def quit(self):
            self.quit_calls += 1

    fake_app = _FakeApp()
    monkeypatch.setattr(
        app_controller_module.QApplication,
        "instance",
        staticmethod(lambda: fake_app),
    )
    monkeypatch.setattr(
        c,
        "_download_update_installer",
        lambda url, version: {"path": "C:/tmp/AiringDeck-Setup-3.4.0.exe"},
    )
    monkeypatch.setattr(c, "_launch_downloaded_installer", lambda path: launched.__setitem__("path", path))

    c.startUpdateInstall()

    assert launched["path"].endswith("AiringDeck-Setup-3.4.0.exe")
    assert fake_app.quit_calls == 1
    assert c.updateInstallInProgress is False


def test_integration_start_update_install_no_url(monkeypatch):
    c = _make_controller(monkeypatch, update_service_cls=FakeNoUpdateService)
    launched = {"count": 0}

    monkeypatch.setattr(
        c,
        "_launch_downloaded_installer",
        lambda _path: launched.__setitem__("count", launched["count"] + 1),
    )

    c.startUpdateInstall()

    assert launched["count"] == 0
    assert "Link aggiornamento non disponibile" in c.statusMessage
