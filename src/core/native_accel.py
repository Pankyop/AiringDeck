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
