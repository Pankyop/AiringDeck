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

