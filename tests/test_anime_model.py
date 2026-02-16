from core.anime_model import AnimeModel


def _entry(media_id, title="T", progress=0, airing="TBA", is_today=False):
    return {
        "media": {"id": media_id, "title": {"romaji": title}},
        "display_title": title,
        "progress": progress,
        "airing_time_formatted": airing,
        "is_today": is_today,
    }


def test_model_populates_and_reads_roles():
    model = AnimeModel()
    entries = [_entry(1, "One", 3, "10:00", True), _entry(2, "Two", 4, "11:00", False)]

    model.update_data(entries)

    assert model.rowCount() == 2
    assert model.count == 2
    idx0 = model.index(0, 0)
    idx1 = model.index(1, 0)
    assert model.data(idx0, model.DisplayTitleRole) == "One"
    assert model.data(idx0, model.ProgressRole) == 3
    assert model.data(idx1, model.DisplayTitleRole) == "Two"
    assert model.data(idx1, model.IsTodayRole) is False


def test_model_updates_data_without_structure_change():
    model = AnimeModel()
    initial = [_entry(1, "One", 1), _entry(2, "Two", 2)]
    changed = [_entry(1, "ONE", 9), _entry(2, "TWO", 8)]

    model.update_data(initial)
    model.update_data(changed)

    assert model.rowCount() == 2
    assert model.data(model.index(0, 0), model.DisplayTitleRole) == "ONE"
    assert model.data(model.index(1, 0), model.ProgressRole) == 8

