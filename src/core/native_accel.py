from __future__ import annotations

from typing import Any

try:
    from core import _airingdeck_native as _native
except Exception:
    _native = None


def is_native_available() -> bool:
    return _native is not None


def filter_entries(entries: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    if not query:
        return entries

    if _native is None:
        return [entry for entry in entries if query in entry.get("_search_blob", "")]

    try:
        indices = _native.filter_contains_indices(entries, query)
    except Exception:
        return [entry for entry in entries if query in entry.get("_search_blob", "")]

    return [entries[i] for i in indices]


def filter_entries_advanced(
    entries: list[dict[str, Any]],
    query: str,
    selected_genre: str,
    min_score: int,
    only_today: bool,
    today_weekday: int,
) -> list[dict[str, Any]]:
    query = (query or "").strip()
    selected_genre = (selected_genre or "").strip().lower()
    min_score = int(min_score or 0)
    only_today = bool(only_today)
    today_weekday = int(today_weekday)

    if _native is None:
        return _filter_entries_advanced_python(
            entries, query, selected_genre, min_score, only_today, today_weekday
        )

    try:
        indices = _native.filter_advanced_indices(
            entries,
            query,
            selected_genre,
            min_score,
            1 if only_today else 0,
            today_weekday,
        )
    except Exception:
        return _filter_entries_advanced_python(
            entries, query, selected_genre, min_score, only_today, today_weekday
        )

    return [entries[i] for i in indices]


def _filter_entries_advanced_python(
    entries: list[dict[str, Any]],
    query: str,
    selected_genre: str,
    min_score: int,
    only_today: bool,
    today_weekday: int,
) -> list[dict[str, Any]]:
    filtered = entries

    if query:
        filtered = [entry for entry in filtered if query in entry.get("_search_blob", "")]

    if selected_genre and selected_genre != "all genres":
        filtered = [
            entry
            for entry in filtered
            if any((g or "").lower() == selected_genre for g in entry.get("media", {}).get("genres", []))
        ]

    if min_score > 0:
        filtered = [
            entry
            for entry in filtered
            if (entry.get("media", {}).get("averageScore") or 0) >= min_score
        ]

    if only_today:
        filtered = [entry for entry in filtered if int(entry.get("calendar_day", -1)) == today_weekday]

    return filtered
