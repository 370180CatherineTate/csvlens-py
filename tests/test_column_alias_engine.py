"""Tests for ColumnAliasEngine."""

import pytest

from csvlens.column_alias_engine import ColumnAliasEngine


@pytest.fixture
def engine() -> ColumnAliasEngine:
    return ColumnAliasEngine(["name", "age", "email"])


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnAliasEngine([])


def test_headers_property(engine: ColumnAliasEngine):
    assert engine.headers == ["name", "age", "email"]


def test_initial_no_aliases(engine: ColumnAliasEngine):
    assert engine.aliases == {}


def test_display_headers_no_aliases(engine: ColumnAliasEngine):
    assert engine.display_headers() == ["name", "age", "email"]


def test_set_alias(engine: ColumnAliasEngine):
    engine.set_alias("name", "Full Name")
    assert engine.display_name("name") == "Full Name"


def test_set_alias_updates_display_headers(engine: ColumnAliasEngine):
    engine.set_alias("age", "Years")
    assert engine.display_headers() == ["name", "Years", "email"]


def test_set_alias_unknown_column_raises(engine: ColumnAliasEngine):
    with pytest.raises(KeyError):
        engine.set_alias("nonexistent", "X")


def test_set_alias_empty_string_raises(engine: ColumnAliasEngine):
    with pytest.raises(ValueError):
        engine.set_alias("name", "   ")


def test_set_alias_duplicate_alias_raises(engine: ColumnAliasEngine):
    engine.set_alias("name", "Label")
    with pytest.raises(ValueError, match="already assigned"):
        engine.set_alias("age", "Label")


def test_set_alias_same_column_overwrite_allowed(engine: ColumnAliasEngine):
    engine.set_alias("name", "Label")
    engine.set_alias("name", "Label")  # should not raise
    assert engine.display_name("name") == "Label"


def test_remove_alias(engine: ColumnAliasEngine):
    engine.set_alias("name", "Full Name")
    engine.remove_alias("name")
    assert engine.display_name("name") == "name"


def test_remove_alias_no_alias_is_noop(engine: ColumnAliasEngine):
    engine.remove_alias("name")  # no alias set — should not raise
    assert engine.display_name("name") == "name"


def test_remove_alias_unknown_column_raises(engine: ColumnAliasEngine):
    with pytest.raises(KeyError):
        engine.remove_alias("ghost")


def test_clear_aliases(engine: ColumnAliasEngine):
    engine.set_alias("name", "N")
    engine.set_alias("age", "A")
    engine.clear_aliases()
    assert engine.aliases == {}
    assert engine.display_headers() == ["name", "age", "email"]


def test_display_name_unknown_column_raises(engine: ColumnAliasEngine):
    with pytest.raises(KeyError):
        engine.display_name("unknown")


def test_resolve_alias_to_original(engine: ColumnAliasEngine):
    engine.set_alias("email", "E-Mail")
    assert engine.resolve("E-Mail") == "email"


def test_resolve_original_name_when_no_alias(engine: ColumnAliasEngine):
    assert engine.resolve("age") == "age"


def test_resolve_unknown_returns_none(engine: ColumnAliasEngine):
    assert engine.resolve("does_not_exist") is None
