import core.native_accel as native_accel


def _entries():
    return [
        {"_search_blob": "one piece"},
        {"_search_blob": "oshi no ko"},
        {"_search_blob": "jujutsu kaisen"},
    ]


def test_filter_entries_python_fallback(monkeypatch):
    monkeypatch.setattr(native_accel, "_native", None)
    data = _entries()

    out = native_accel.filter_entries(data, "ko")

    assert len(out) == 1
    assert out[0]["_search_blob"] == "oshi no ko"


def test_filter_entries_native_path(monkeypatch):
    class FakeNative:
        @staticmethod
        def filter_contains_indices(entries, query):
            assert query == "ju"
            return [2]

    monkeypatch.setattr(native_accel, "_native", FakeNative())
    data = _entries()

    out = native_accel.filter_entries(data, "ju")

    assert len(out) == 1
    assert out[0]["_search_blob"] == "jujutsu kaisen"


def test_filter_entries_advanced_python_fallback(monkeypatch):
    monkeypatch.setattr(native_accel, "_native", None)
    data = [
        {
            "_search_blob": "one piece",
            "calendar_day": 1,
            "media": {"genres": ["Action"], "averageScore": 82},
        },
        {
            "_search_blob": "oshi no ko",
            "calendar_day": 2,
            "media": {"genres": ["Drama"], "averageScore": 91},
        },
    ]

    out = native_accel.filter_entries_advanced(
        data,
        query="ko",
        selected_genre="drama",
        min_score=90,
        only_today=True,
        today_weekday=2,
    )

    assert len(out) == 1
    assert out[0]["_search_blob"] == "oshi no ko"


def test_filter_entries_advanced_native_path(monkeypatch):
    class FakeNative:
        @staticmethod
        def filter_advanced_indices(entries, query, selected_genre, min_score, only_today, today_weekday):
            assert query == "one"
            assert selected_genre == "action"
            assert min_score == 70
            assert only_today == 0
            assert today_weekday == 1
            return [0]

    monkeypatch.setattr(native_accel, "_native", FakeNative())
    data = [
        {"_search_blob": "one piece", "calendar_day": 1, "media": {"genres": ["Action"], "averageScore": 80}},
        {"_search_blob": "jujutsu kaisen", "calendar_day": 1, "media": {"genres": ["Action"], "averageScore": 95}},
    ]

    out = native_accel.filter_entries_advanced(
        data,
        query="one",
        selected_genre="action",
        min_score=70,
        only_today=False,
        today_weekday=1,
    )

    assert len(out) == 1
    assert out[0]["_search_blob"] == "one piece"
