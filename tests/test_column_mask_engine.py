"""Tests for ColumnMaskEngine and ColumnMaskRenderer."""
import pytest

from csvlens.column_mask_engine import ColumnMaskEngine
from csvlens.column_mask_renderer import ColumnMaskRenderer


HEADERS = ["name", "email", "age", "salary"]

ROWS = [
    {"name": "Alice", "email": "alice@example.com", "age": "30", "salary": "70000"},
    {"name": "Bob",   "email": "bob@example.com",   "age": "25", "salary": "55000"},
]


@pytest.fixture
def engine() -> ColumnMaskEngine:
    return ColumnMaskEngine(HEADERS)


@pytest.fixture
def renderer(engine: ColumnMaskEngine) -> ColumnMaskRenderer:
    return ColumnMaskRenderer(engine, col_width=16)


# --- ColumnMaskEngine ---

def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnMaskEngine([])


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == HEADERS


def test_initial_no_masked(engine):
    assert engine.masked_columns == []


def test_mask_column(engine):
    engine.mask("email")
    assert "email" in engine.masked_columns


def test_mask_invalid_column_raises(engine):
    with pytest.raises(KeyError):
        engine.mask("nonexistent")


def test_unmask_column(engine):
    engine.mask("email")
    engine.unmask("email")
    assert "email" not in engine.masked_columns


def test_unmask_invalid_column_raises(engine):
    with pytest.raises(KeyError):
        engine.unmask("nonexistent")


def test_clear_removes_all(engine):
    engine.mask("email")
    engine.mask("salary")
    engine.clear()
    assert engine.masked_columns == []


def test_default_mask_placeholder(engine):
    engine.mask("email")
    result = engine.apply(ROWS[0])
    assert result["email"] == ColumnMaskEngine.DEFAULT_MASK
    assert result["name"] == "Alice"  # unmasked


def test_custom_placeholder(engine):
    engine.mask("salary", placeholder="[REDACTED]")
    result = engine.apply(ROWS[0])
    assert result["salary"] == "[REDACTED]"


def test_apply_rows(engine):
    engine.mask("email")
    results = engine.apply_rows(ROWS)
    assert all(r["email"] == ColumnMaskEngine.DEFAULT_MASK for r in results)
    assert results[0]["name"] == "Alice"


def test_is_masked(engine):
    assert not engine.is_masked("email")
    engine.mask("email")
    assert engine.is_masked("email")


# --- ColumnMaskRenderer ---

def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError):
        ColumnMaskRenderer(engine, col_width=2)


def test_col_width_property(renderer):
    assert renderer.col_width == 16


def test_render_header_returns_string(renderer):
    assert isinstance(renderer.render_header(), str)


def test_render_header_contains_columns(renderer):
    header = renderer.render_header()
    for h in HEADERS:
        assert h in header


def test_render_row_returns_string(renderer):
    assert isinstance(renderer.render_row(ROWS[0]), str)


def test_render_row_masks_value(engine, renderer):
    engine.mask("email")
    row_str = renderer.render_row(ROWS[0])
    assert ColumnMaskEngine.DEFAULT_MASK in row_str
    assert "alice@example.com" not in row_str


def test_render_all_includes_header_and_rows(engine, renderer):
    engine.mask("salary")
    output = renderer.render_all(ROWS)
    lines = output.splitlines()
    assert len(lines) == 3  # header + 2 rows
    assert "salary" in lines[0]
