import pytest
from csvlens.column_diff_profile import ColumnDiffProfile

HEADERS = ["name", "age", "city"]

ROWS_A = [
    {"name": "Alice", "age": "30", "city": "NY"},
    {"name": "Bob", "age": "25", "city": "LA"},
]
ROWS_B = [
    {"name": "Alice", "age": "31", "city": "NY"},
    {"name": "Bob", "age": "25", "city": "SF"},
]


@pytest.fixture
def profile():
    return ColumnDiffProfile(HEADERS)


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnDiffProfile([])


def test_headers_property(profile):
    assert profile.headers == HEADERS


def test_headers_returns_copy(profile):
    h = profile.headers
    h.append("extra")
    assert "extra" not in profile.headers


def test_initial_no_snapshots(profile):
    assert profile.snapshot_names == []


def test_save_snapshot(profile):
    profile.save_snapshot("snap1", ROWS_A)
    assert "snap1" in profile.snapshot_names


def test_blank_name_raises(profile):
    with pytest.raises(ValueError):
        profile.save_snapshot("  ", ROWS_A)


def test_delete_snapshot(profile):
    profile.save_snapshot("snap1", ROWS_A)
    profile.delete_snapshot("snap1")
    assert "snap1" not in profile.snapshot_names


def test_delete_nonexistent_is_noop(profile):
    profile.delete_snapshot("ghost")


def test_compare_missing_snapshot_raises(profile):
    profile.save_snapshot("snap1", ROWS_A)
    with pytest.raises(KeyError):
        profile.compare("snap1", "missing")


def test_compare_detects_diffs(profile):
    profile.save_snapshot("a", ROWS_A)
    profile.save_snapshot("b", ROWS_B)
    result = profile.compare("a", "b")
    assert result["age"] == [0]
    assert result["city"] == [1]
    assert result["name"] == []


def test_diff_summary_counts(profile):
    profile.save_snapshot("a", ROWS_A)
    profile.save_snapshot("b", ROWS_B)
    summary = profile.diff_summary("a", "b")
    assert summary["age"] == 1
    assert summary["city"] == 1
    assert summary["name"] == 0


def test_compare_identical_snapshots(profile):
    profile.save_snapshot("a", ROWS_A)
    profile.save_snapshot("b", ROWS_A)
    result = profile.compare("a", "b")
    assert all(len(v) == 0 for v in result.values())
