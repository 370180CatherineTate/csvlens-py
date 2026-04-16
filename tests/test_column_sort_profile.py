"""Tests for ColumnSortProfile and SortProfile."""
import pytest

from csvlens.column_sort_profile import ColumnSortProfile, SortProfile


HEADERS = ["name", "age", "city"]


@pytest.fixture
def profile():
    return ColumnSortProfile(HEADERS)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnSortProfile([])


def test_headers_property(profile):
    assert profile.headers == HEADERS


def test_headers_returns_copy(profile):
    h = profile.headers
    h.append("extra")
    assert profile.headers == HEADERS


def test_initial_no_profiles(profile):
    assert profile.profile_names == []


def test_initial_active_is_none(profile):
    assert profile.active_profile is None


def test_save_profile(profile):
    profile.save("alpha", [("name", True), ("age", False)])
    assert "alpha" in profile.profile_names


def test_save_invalid_column_raises(profile):
    with pytest.raises(KeyError, match="not in headers"):
        profile.save("bad", [("unknown", True)])


def test_save_empty_name_raises(profile):
    with pytest.raises(ValueError, match="profile name"):
        profile.save("", [("name", True)])


def test_activate_sets_active(profile):
    profile.save("p1", [("age", True)])
    sp = profile.activate("p1")
    assert profile.active_profile == "p1"
    assert sp.name == "p1"


def test_activate_nonexistent_raises(profile):
    with pytest.raises(KeyError, match="does not exist"):
        profile.activate("ghost")


def test_deactivate_clears_active(profile):
    profile.save("p1", [("age", True)])
    profile.activate("p1")
    profile.deactivate()
    assert profile.active_profile is None


def test_active_keys_empty_when_none_active(profile):
    profile.save("p1", [("age", True)])
    assert profile.active_keys() == []


def test_active_keys_returns_keys(profile):
    keys = [("name", True), ("age", False)]
    profile.save("p1", keys)
    profile.activate("p1")
    assert profile.active_keys() == keys


def test_delete_profile(profile):
    profile.save("p1", [("age", True)])
    profile.delete("p1")
    assert "p1" not in profile.profile_names


def test_delete_active_profile_clears_active(profile):
    profile.save("p1", [("age", True)])
    profile.activate("p1")
    profile.delete("p1")
    assert profile.active_profile is None


def test_delete_nonexistent_raises(profile):
    with pytest.raises(KeyError):
        profile.delete("ghost")


def test_sort_profile_description_empty():
    sp = SortProfile(name="empty")
    assert "empty" in sp.description()


def test_sort_profile_description_with_keys():
    sp = SortProfile(name="s", keys=[("age", True), ("name", False)])
    desc = sp.description()
    assert "ASC" in desc
    assert "DESC" in desc
