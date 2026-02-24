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


class DummyAuthService(QObject):
    auth_completed = Signal(str)
    auth_failed = Signal(str)

    def __init__(self):
        super().__init__()

    def get_saved_token(self):
        return None

    def clear_token(self):
        return None

    def start_auth_flow(self):
        return None


class DummyAniListService:
    def __init__(self):
        self._token = None

    def set_token(self, token):
        self._token = token

    def get_viewer_info(self):
        return {}

    def get_watching_anime(self, user_id):
        now = datetime.now()
        return [
            {
                "media": {
                    "id": 10,
                    "title": {"romaji": "Shirobako", "english": "SHIROBAKO"},
                    "genres": ["Drama"],
                    "averageScore": 90,
                    "nextAiringEpisode": {
                        "episode": 2,
                        "airingAt": int((now + timedelta(hours=1)).timestamp()),
                        "timeUntilAiring": 0,
                    },
                    "coverImage": {"large": "", "medium": ""},
                },
                "progress": 1,
            }
        ]


def _controller(monkeypatch):
    FakeSettings._store = {}
    monkeypatch.setattr(app_controller_module, "QSettings", FakeSettings)
    monkeypatch.setattr(app_controller_module, "AuthService", DummyAuthService)
    monkeypatch.setattr(app_controller_module, "AniListService", DummyAniListService)
    monkeypatch.setattr(app_controller_module.AppController, "_init_tray_icon", lambda self: None)
    c = app_controller_module.AppController(None)
    c._update_timer.stop()
    c._filter_update_timer.stop()
    c._sync_retry_timer.stop()
    return c


def test_language_messages_switch(monkeypatch):
    c = _controller(monkeypatch)
    assert c._msg_ready() == "Pronto"
    assert c._msg_logged_out() == "Disconnesso"

    c.appLanguage = "en"
    assert c._msg_ready() == "Ready"
    assert c._msg_logged_out() == "Logged out"

    c.appLanguage = "xx"
    assert c._msg_ready() == "Pronto"


def test_use_english_title_updates_selected_entry(monkeypatch):
    c = _controller(monkeypatch)
    c._on_anime_list_result(DummyAniListService().get_watching_anime(1))

    c.selectAnime(10)
    assert c.selectedAnime["display_title"] == "Shirobako"

    c.useEnglishTitle = True
    assert c.selectedAnime["display_title"] == "SHIROBAKO"


def test_notifications_label_translation(monkeypatch):
    c = _controller(monkeypatch)
    assert c._tr("Notifica di prova", "Test notification") == "Notifica di prova"
    c.appLanguage = "en"
    assert c._tr("Notifica di prova", "Test notification") == "Test notification"
