"""Tests for DiffRenderer."""
import pytest
from csvlens.diff_engine import DiffEngine
from csvlens.diff_renderer import DiffRenderer

HEADERS = ["id", "name", "score"]


@pytest.fixture
def renderer():
    return DiffRenderer(col_width=15, use_color=False)


@pytest.fixture
def engine():
    return DiffEngine(HEADERS, key_column="id")


def test_invalid_col_width_raises():
    with pytest.raises(ValueError, match="col_width"):
        DiffRenderer(col_width=2)


def test_render_returns_string(renderer, engine):
    result = engine.compute([], [])
    output = renderer.render(result)
    assert isinstance(output, str)


def test_render_summary_line_present(renderer, engine):
    result = engine.compute([], [])
    output = renderer.render(result)
    assert "Diff summary" in output


def test_render_added_row(renderer, engine):
    curr = [{"id": "1", "name": "Alice", "score": "90"}]
    result = engine.compute([], curr)
    output = renderer.render(result)
    assert "+" in output
    assert "Alice" in output


def test_render_removed_row(renderer, engine):
    base = [{"id": "1", "name": "Alice", "score": "90"}]
    result = engine.compute(base, [])
    output = renderer.render(result)
    assert "-" in output
    assert "Alice" in output


def test_render_changed_row(renderer, engine):
    base = [{"id": "1", "name": "Alice", "score": "90"}]
    curr = [{"id": "1", "name": "Alice", "score": "99"}]
    result = engine.compute(base, curr)
    output = renderer.render(result)
    assert "~" in output
    assert "OLD" in output
    assert "NEW" in output
    assert "90" in output
    assert "99" in output


def test_render_str_alias(renderer, engine):
    result = engine.compute([], [])
    assert renderer.render_str(result) == renderer.render(result)


def test_long_value_truncated(engine):
    r = DiffRenderer(col_width=6, use_color=False)
    curr = [{"id": "1", "name": "VeryLongNameHere", "score": "90"}]
    result = engine.compute([], curr)
    output = r.render(result)
    assert "VeryL…" in output


def test_color_codes_absent_when_disabled(engine):
    r = DiffRenderer(use_color=False)
    base = [{"id": "1", "name": "Alice", "score": "90"}]
    result = engine.compute(base, [])
    output = r.render(result)
    assert "\033[" not in output


def test_color_codes_present_when_enabled(engine):
    r = DiffRenderer(use_color=True)
    base = [{"id": "1", "name": "Alice", "score": "90"}]
    result = engine.compute(base, [])
    output = r.render(result)
    assert "\033[" in output
