from hypothesis import given, strategies as st

import core.native_accel as native_accel


@given(
    blobs=st.lists(st.text(min_size=0, max_size=30), min_size=0, max_size=40),
    query=st.text(min_size=0, max_size=10),
)
def test_filter_entries_matches_reference_python(blobs, query):
    old_native = native_accel._native
    native_accel._native = None
    entries = [{"_search_blob": b} for b in blobs]

    try:
        expected = [entry for entry in entries if query in entry.get("_search_blob", "")]
        actual = native_accel.filter_entries(entries, query)
    finally:
        native_accel._native = old_native

    assert actual == expected
