"""Tests for ColumnGroupEngine and ColumnGroupRenderer."""

import pytest
from csvlens.column_group_engine import ColumnGroupEngine
from csvlens.column_group_renderer import ColumnGroupRenderer


@pytest.fixture
def engine():
    return ColumnGroupEngine(["id", "first_name", "last_name", "age", "city", "country"])


# ── ColumnGroupEngine ──────────────────────────────────────────────────────────

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnGroupEngine([])


def test_headers_property(engine):
    assert engine.headers == ["id", "first_name", "last_name", "age", "city", "country"]


def test_initial_no_groups(engine):
    assert engine.groups == {}
    assert engine.group_names == []


def test_add_group(engine):
    engine.add_group("name", ["first_name", "last_name"])
    assert "name" in engine.groups
    assert engine.groups["name"] == ["first_name", "last_name"]


def test_add_group_unknown_column_raises(engine):
    with pytest.raises(ValueError, match="unknown columns"):
        engine.add_group("bad", ["first_name", "nonexistent"])


def test_add_group_empty_name_raises(engine):
    with pytest.raises(ValueError, match="non-empty string"):
        engine.add_group("", ["age"])


def test_add_group_empty_columns_raises(engine):
    with pytest.raises(ValueError, match="columns list must not be empty"):
        engine.add_group("g", [])


def test_remove_group(engine):
    engine.add_group("loc", ["city", "country"])
    engine.remove_group("loc")
    assert "loc" not in engine.groups


def test_remove_nonexistent_group_raises(engine):
    with pytest.raises(KeyError):
        engine.remove_group("ghost")


def test_collapse_and_is_collapsed(engine):
    engine.add_group("name", ["first_name", "last_name"])
    assert not engine.is_collapsed("name")
    engine.collapse("name")
    assert engine.is_collapsed("name")


def test_expand_clears_collapsed(engine):
    engine.add_group("name", ["first_name", "last_name"])
    engine.collapse("name")
    engine.expand("name")
    assert not engine.is_collapsed("name")


def test_collapse_nonexistent_raises(engine):
    with pytest.raises(KeyError):
        engine.collapse("nope")


def test_visible_headers_no_groups(engine):
    assert engine.visible_headers() == engine.headers


def test_visible_headers_collapsed(engine):
    engine.add_group("name", ["first_name", "last_name"])
    engine.collapse("name")
    visible = engine.visible_headers()
    assert "[name]" in visible
    assert "first_name" not in visible
    assert "last_name" not in visible
    assert "id" in visible


def test_visible_headers_expanded_shows_all(engine):
    engine.add_group("name", ["first_name", "last_name"])
    # expanded by default
    assert engine.visible_headers() == engine.headers


def test_group_for_column(engine):
    engine.add_group("loc", ["city", "country"])
    assert engine.group_for_column("city") == "loc"
    assert engine.group_for_column("age") is None


# ── ColumnGroupRenderer ────────────────────────────────────────────────────────

@pytest.fixture
def renderer(engine):
    return ColumnGroupRenderer(engine, col_width=12)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width"):
        ColumnGroupRenderer(engine, col_width=2)


def test_render_header_returns_string(renderer):
    assert isinstance(renderer.render_header(), str)


def test_render_header_contains_column(renderer):
    assert "id" in renderer.render_header()


def test_render_placeholder_in_header(engine):
    engine.add_group("name", ["first_name", "last_name"])
    engine.collapse("name")
    r = ColumnGroupRenderer(engine, col_width=14)
    header = r.render_header()
    assert "[name]" in header


def test_render_group_summary_no_groups(renderer):
    summary = renderer.render_group_summary()
    assert "no groups" in summary


def test_render_group_summary_with_group(engine):
    engine.add_group("loc", ["city", "country"])
    r = ColumnGroupRenderer(engine)
    summary = r.render_group_summary()
    assert "loc" in summary
    assert "expanded" in summary


def test_render_returns_combined_string(renderer):
    result = renderer.render()
    assert "\n" in result
