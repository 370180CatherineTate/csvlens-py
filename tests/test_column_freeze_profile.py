"""Tests for ColumnFreezeProfile."""
import pytest
from csvlens.column_freeze_profile import ColumnFreezeProfile


@pytest.fixture
def profile():
    return ColumnFreezeProfile(["id", "name", "age", "city"])


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnFreezeProfile([])


def test_headers_property(profile):
    assert profile.headers == ["id", "name", "age", "city"]


def test_headers_returns_copy(profile):
    h = profile.headers
    h.append("extra")
    assert "extra" not in profile.headers


def test_initial_no_profiles(profile):
    assert profile.profile_names == []


def test_initial_active_is_none(profile):
    assert profile.active_profile is None


def test_save_profile(profile):
    profile.save("left", ["id", "name"])
    assert "left" in profile.profile_names


def test_save_invalid_column_raises(profile):
    with pytest.raises(ValueError):
        profile.save("bad", ["nonexistent"])


def test_save_empty_name_raises(profile):
    with pytest.raises(ValueError):
        profile.save("", ["id"])


def test_save_whitespace_name_raises(profile):
    with pytest.raises(ValueError):
        profile.save("   ", ["id"])


def test_get_profile(profile):
    profile.save("left", ["id", "name"])
    assert profile.get("left") == ["id", "name"]


def test_get_missing_profile_raises(profile):
    with pytest.raises(KeyError):
        profile.get("nope")


def test_activate_sets_active(profile):
    profile.save("left", ["id"])
    frozen = profile.activate("left")
    assert profile.active_profile == "left"
    assert frozen == ["id"]


def test_activate_missing_raises(profile):
    with pytest.raises(KeyError):
        profile.activate("ghost")


def test_deactivate_clears_active(profile):
    profile.save("left", ["id"])
    profile.activate("left")
    profile.deactivate()
    assert profile.active_profile is None


def test_delete_profile(profile):
    profile.save("left", ["id"])
    profile.delete("left")
    assert "left" not in profile.profile_names


def test_delete_active_clears_active(profile):
    profile.save("left", ["id"])
    profile.activate("left")
    profile.delete("left")
    assert profile.active_profile is None


def test_delete_missing_raises(profile):
    with pytest.raises(KeyError):
        profile.delete("ghost")


def test_save_overwrites_existing(profile):
    profile.save("left", ["id"])
    profile.save("left", ["id", "name"])
    assert profile.get("left") == ["id", "name"]
    assert profile.profile_names.count("left") == 1
