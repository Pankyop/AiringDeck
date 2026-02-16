from datetime import datetime, timedelta

from PySide6.QtCore import QObject, Signal

import core.app_controller as app_controller_module


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
    def set_token(self, token):
        return None

    def get_viewer_info(self):
        return {}

    def get_watching_anime(self, user_id):
        return []


def _entry(media_id, title, day_offset, genres, score, progress):
    airing_at = int((datetime.now() + timedelta(days=day_offset)).timestamp())
    return {
        "media": {
            "id": media_id,
            "title": {"romaji": title, "english": title},
            "genres": genres,
            "averageScore": score,
            "nextAiringEpisode": {"episode": progress + 1, "airingAt": airing_at, "timeUntilAiring": 0},
            "coverImage": {"large": "", "medium": ""},
        },
        "progress": progress,
    }


def _controller(monkeypatch):
    monkeypatch.setattr(app_controller_module, "AuthService", DummyAuthService)
    monkeypatch.setattr(app_controller_module, "AniListService", DummyAniListService)
    controller = app_controller_module.AppController(None)
    controller.resetAllFilters()
    return controller


def test_genre_and_score_filters(monkeypatch):
    c = _controller(monkeypatch)
    data = [
        _entry(1, "One", 0, ["Action"], 80, 2),
        _entry(2, "Two", 0, ["Drama"], 60, 4),
        _entry(3, "Three", 1, ["Action"], 90, 1),
    ]
    c._on_anime_list_result(data)

    c.selectedGenre = "Action"
    c.minScore = 85

    model = c.allAnimeModel
    assert model.rowCount() == 1
    assert model.get_entry(0)["media"]["id"] == 3


def test_sort_by_progress_desc(monkeypatch):
    c = _controller(monkeypatch)
    data = [
        _entry(1, "One", 0, ["Action"], 80, 2),
        _entry(2, "Two", 0, ["Drama"], 60, 6),
        _entry(3, "Three", 0, ["Action"], 90, 4),
    ]
    c._on_anime_list_result(data)

    c.sortField = "progress"
    c.sortAscending = False

    model = c.allAnimeModel
    ids = [model.get_entry(i)["media"]["id"] for i in range(model.rowCount())]
    assert ids == [2, 3, 1]
