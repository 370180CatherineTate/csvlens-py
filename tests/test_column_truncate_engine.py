"""Tests for ColumnTruncateEngine and ColumnTruncateRenderer."""

import pytest

from csvlens.column_truncate_engine import ColumnTruncateEngine
from csvlens.column_truncate_renderer import ColumnTruncateRenderer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def engine() -> ColumnTruncateEngine:
    return ColumnTruncateEngine(["name", "description", "tag"], default_max_len=10)


@pytest.fixture
def renderer(engine: ColumnTruncateEngine) -> ColumnTruncateRenderer:
    return ColumnTruncateRenderer(engine, col_width=12)


# ---------------------------------------------------------------------------
# ColumnTruncateEngine – construction guards
# ---------------------------------------------------------------------------

def test_empty_headers_raises() -> None:
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnTruncateEngine([])


def test_default_max_len_too_small_raises() -> None:
    with pytest.raises(ValueError, match="default_max_len"):
        ColumnTruncateEngine(["a"], default_max_len=3)


# ---------------------------------------------------------------------------
# ColumnTruncateEngine – properties
# ---------------------------------------------------------------------------

def test_headers_property(engine: ColumnTruncateEngine) -> None:
    assert engine.headers == ["name", "description", "tag"]


def test_headers_returns_copy(engine: ColumnTruncateEngine) -> None:
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_default_max_len_property(engine: ColumnTruncateEngine) -> None:
    assert engine.default_max_len == 10


def test_initial_no_overrides(engine: ColumnTruncateEngine) -> None:
    assert engine.overrides == {}


# ---------------------------------------------------------------------------
# ColumnTruncateEngine – overrides
# ---------------------------------------------------------------------------

def test_set_override(engine: ColumnTruncateEngine) -> None:
    engine.set_override("name", 8)
    assert engine.overrides["name"] == 8


def test_set_override_unknown_column_raises(engine: ColumnTruncateEngine) -> None:
    with pytest.raises(KeyError, match="unknown_col"):
        engine.set_override("unknown_col", 8)


def test_set_override_too_small_raises(engine: ColumnTruncateEngine) -> None:
    with pytest.raises(ValueError, match="max_len"):
        engine.set_override("name", 2)


def test_clear_override(engine: ColumnTruncateEngine) -> None:
    engine.set_override("name", 8)
    engine.clear_override("name")
    assert "name" not in engine.overrides


def test_clear_all_overrides(engine: ColumnTruncateEngine) -> None:
    engine.set_override("name", 8)
    engine.set_override("tag", 6)
    engine.clear_all_overrides()
    assert engine.overrides == {}


# ---------------------------------------------------------------------------
# ColumnTruncateEngine – truncation logic
# ---------------------------------------------------------------------------

def test_short_value_unchanged(engine: ColumnTruncateEngine) -> None:
    assert engine.truncate("name", "Alice") == "Alice"


def test_exact_length_unchanged(engine: ColumnTruncateEngine) -> None:
    assert engine.truncate("name", "A" * 10) == "A" * 10


def test_long_value_truncated(engine: ColumnTruncateEngine) -> None:
    result = engine.truncate("name", "A" * 20)
    assert result.endswith("...")
    assert len(result) == 10


def test_override_respected(engine: ColumnTruncateEngine) -> None:
    engine.set_override("description", 6)
    result = engine.truncate("description", "Hello World")
    assert len(result) == 6
    assert result.endswith("...")


def test_truncate_row(engine: ColumnTruncateEngine) -> None:
    row = {"name": "X" * 20, "description": "short", "tag": "Y" * 15}
    result = engine.truncate_row(row)
    assert len(result["name"]) == 10
    assert result["description"] == "short"
    assert len(result["tag"]) == 10


# ---------------------------------------------------------------------------
# ColumnTruncateRenderer
# ---------------------------------------------------------------------------

def test_invalid_col_width_raises(engine: ColumnTruncateEngine) -> None:
    with pytest.raises(ValueError, match="col_width"):
        ColumnTruncateRenderer(engine, col_width=2)


def test_col_width_property(renderer: ColumnTruncateRenderer) -> None:
    assert renderer.col_width == 12


def test_render_header_returns_string(renderer: ColumnTruncateRenderer) -> None:
    assert isinstance(renderer.render_header(), str)


def test_render_header_contains_columns(renderer: ColumnTruncateRenderer) -> None:
    header = renderer.render_header()
    assert "name" in header
    assert "description" in header


def test_render_row_returns_string(renderer: ColumnTruncateRenderer) -> None:
    row = {"name": "Alice", "description": "A long description text", "tag": "csv"}
    assert isinstance(renderer.render_row(row), str)


def test_render_all_includes_header_and_rows(renderer: ColumnTruncateRenderer) -> None:
    rows = [
        {"name": "Alice", "description": "Short", "tag": "t1"},
        {"name": "Bob", "description": "Another very long description here", "tag": "t2"},
    ]
    output = renderer.render_all(rows)
    lines = output.splitlines()
    assert len(lines) == 3  # header + 2 rows
    assert "name" in lines[0]
