"""Tests for ColumnVisibilityProfile."""
import pytest

from csvlens.column_visibility_profile import ColumnVisibilityProfile


HEADERS = ["id", "name", "age", "email", "score"]


@pytest.fixture
def profile():
    return ColumnVisibilityProfile(HEADERS)


# --- construction ---

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="empty"):
        ColumnVisibilityProfile([])


def test_headers_property(profile):
    assert profile.headers == HEADERS


def test_initial_no_profiles(profile):
    assert profile.profile_names == []


def test_initial_active_is_none(profile):
    assert profile.active_profile is None


# --- save ---

def test_save_creates_profile(profile):
    profile.save("minimal", ["id", "name"])
    assert "minimal" in profile.profile_names


def test_save_empty_name_raises(profile):
    with pytest.raises(ValueError, match="empty"):
        profile.save("", ["id"])


def test_save_unknown_column_raises(profile):
    with pytest.raises(ValueError, match="unknown columns"):
        profile.save("bad", ["id", "nonexistent"])


def test_save_overwrites_existing(profile):
    profile.save("p", ["id"])
    profile.save("p", ["id", "name"])
    assert profile.get("p") == ["id", "name"]


def test_save_empty_visible_list_allowed(profile):
    profile.save("none", [])
    assert profile.get("none") == []


# --- load ---

def test_load_returns_visible_columns(profile):
    profile.save("compact", ["id", "score"])
    result = profile.load("compact")
    assert result == ["id", "score"]


def test_load_sets_active_profile(profile):
    profile.save("compact", ["id", "score"])
    profile.load("compact")
    assert profile.active_profile == "compact"


def test_load_missing_profile_raises(profile):
    with pytest.raises(KeyError, match="ghost"):
        profile.load("ghost")


def test_load_returns_copy(profile):
    profile.save("p", ["id", "name"])
    result = profile.load("p")
    result.append("extra")
    assert profile.get("p") == ["id", "name"]


# --- delete ---

def test_delete_removes_profile(profile):
    profile.save("tmp", ["id"])
    profile.delete("tmp")
    assert "tmp" not in profile.profile_names


def test_delete_clears_active_if_deleted(profile):
    profile.save("tmp", ["id"])
    profile.load("tmp")
    profile.delete("tmp")
    assert profile.active_profile is None


def test_delete_missing_raises(profile):
    with pytest.raises(KeyError, match="ghost"):
        profile.delete("ghost")


def test_delete_does_not_clear_other_active(profile):
    profile.save("a", ["id"])
    profile.save("b", ["name"])
    profile.load("a")
    profile.delete("b")
    assert profile.active_profile == "a"


# --- get ---

def test_get_returns_none_for_missing(profile):
    assert profile.get("nope") is None


def test_get_returns_columns(profile):
    profile.save("full", HEADERS)
    assert profile.get("full") == HEADERS


# --- profile_names sorted ---

def test_profile_names_sorted(profile):
    profile.save("zebra", ["id"])
    profile.save("alpha", ["name"])
    profile.save("middle", ["age"])
    assert profile.profile_names == ["alpha", "middle", "zebra"]
