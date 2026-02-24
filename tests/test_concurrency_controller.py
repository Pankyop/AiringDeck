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


class DeferredThreadPool:
    def __init__(self):
        self._queue = []

    def maxThreadCount(self):
        return 4

    def start(self, worker):
        self._queue.append(worker)

    def pending(self):
        return len(self._queue)

    def run_at(self, index):
        worker = self._queue.pop(index)
        worker.run()

    def run_all(self):
        while self._queue:
            self.run_at(0)


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


def _entry(media_id, title, genres, score, day_offset, progress):
    airing_at = int((datetime.now() + timedelta(days=day_offset, hours=1)).timestamp())
    return {
        "media": {
            "id": media_id,
            "title": {"romaji": title, "english": title},
            "genres": genres,
            "averageScore": score,
            "nextAiringEpisode": {
                "episode": progress + 1,
                "airingAt": airing_at,
                "timeUntilAiring": 0,
            },
            "coverImage": {"large": "", "medium": ""},
        },
        "progress": progress,
    }


class SequenceAniListService:
    def __init__(self):
        self.token = None
        self.calls = 0
        self._payloads = [
            [
                _entry(1, "One Piece", ["Action"], 80, 0, 100),
                _entry(2, "Oshi no Ko", ["Drama"], 92, 0, 4),
            ],
            [
                _entry(2, "Oshi no Ko", ["Drama"], 93, 0, 5),
                _entry(3, "Jujutsu Kaisen", ["Action"], 88, 1, 12),
            ],
            [
                _entry(4, "Frieren", ["Fantasy"], 95, 2, 20),
                _entry(5, "Apothecary Diaries", ["Drama"], 91, 2, 17),
            ],
        ]

    def set_token(self, token):
        self.token = token

    def get_viewer_info(self):
        return {"id": 77, "name": "ketou", "avatar": {"large": "https://example.com/avatar.png"}}

    def get_watching_anime(self, user_id):
        idx = min(self.calls, len(self._payloads) - 1)
        self.calls += 1
        return self._payloads[idx]


def _controller(monkeypatch):
    FakeSettings._store = {}
    monkeypatch.setattr(app_controller_module, "QSettings", FakeSettings)
    monkeypatch.setattr(app_controller_module, "QThreadPool", DeferredThreadPool)
    monkeypatch.setattr(app_controller_module, "AuthService", DummyAuthService)
    monkeypatch.setattr(app_controller_module, "AniListService", SequenceAniListService)
    monkeypatch.setattr(app_controller_module.AppController, "_init_tray_icon", lambda self: None)

    c = app_controller_module.AppController(None)
    c._update_timer.stop()
    c._filter_update_timer.stop()
    c._sync_retry_timer.stop()
    c._is_authenticated = True
    c._user_info = {"id": 77, "name": "ketou", "avatar": "https://example.com/avatar.png"}
    return c


def test_concurrent_sync_requests_interleaved_completion(monkeypatch):
    c = _controller(monkeypatch)
    pool = c._thread_pool

    c.syncAnimeList()
    c.syncAnimeList()
    c.syncAnimeList()
    assert pool.pending() == 1
    assert c._sync_queued is True

    pool.run_all()

    assert c.allAnimeModel.rowCount() == 2
    assert c.isLoading is False
    assert c._anilist_service.calls == 2
    assert "Sincronizzati 2 anime" in c.statusMessage


def test_filters_changed_while_sync_pending_remain_consistent(monkeypatch):
    c = _controller(monkeypatch)
    pool = c._thread_pool

    c.syncAnimeList()
    assert pool.pending() == 1

    c.selectedGenre = "Drama"
    c.minScore = 90
    c.setFilterText("oshi")
    c._apply_pending_filter()

    pool.run_all()

    assert c.allAnimeModel.rowCount() == 1
    assert c.allAnimeModel.get_entry(0)["media"]["id"] == 2


def test_ui_state_mutations_during_pending_sync_do_not_break_models(monkeypatch):
    c = _controller(monkeypatch)
    pool = c._thread_pool

    c.syncAnimeList()
    c.syncAnimeList()
    assert pool.pending() == 1
    assert c._sync_queued is True

    c.onlyToday = True
    c.onlyToday = False
    c.sortField = "score"
    c.sortAscending = False
    c.resetAllFilters()

    pool.run_all()

    assert len(c.dailyCounts) == 7
    assert c.allAnimeModel.rowCount() >= 1
    assert c._anilist_service.calls == 2
