"""Tests for ColumnResizer and ColumnResizeRenderer."""

import pytest

from csvlens.column_resizer import ColumnResizer
from csvlens.column_resize_renderer import ColumnResizeRenderer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def resizer() -> ColumnResizer:
    return ColumnResizer(["name", "age", "city"], default_width=10)


@pytest.fixture()
def renderer(resizer: ColumnResizer) -> ColumnResizeRenderer:
    return ColumnResizeRenderer(resizer)


_SAMPLE_ROWS = [
    {"name": "Alice", "age": "30", "city": "New York"},
    {"name": "Bob", "age": "25", "city": "Los Angeles"},
    {"name": "Charlie", "age": "35", "city": "Chicago"},
]


# ---------------------------------------------------------------------------
# ColumnResizer — construction guards
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers"):
        ColumnResizer([])


def test_min_width_less_than_one_raises():
    with pytest.raises(ValueError, match="min_width"):
        ColumnResizer(["a"], min_width=0)


def test_max_less_than_min_raises():
    with pytest.raises(ValueError, match="max_width"):
        ColumnResizer(["a"], min_width=5, max_width=4)


def test_default_width_out_of_range_raises():
    with pytest.raises(ValueError, match="default_width"):
        ColumnResizer(["a"], min_width=4, max_width=10, default_width=2)


# ---------------------------------------------------------------------------
# ColumnResizer — basic properties
# ---------------------------------------------------------------------------

def test_headers_property(resizer: ColumnResizer):
    assert resizer.headers == ["name", "age", "city"]


def test_get_width_default(resizer: ColumnResizer):
    assert resizer.get_width("name") == 10


def test_get_width_unknown_raises(resizer: ColumnResizer):
    with pytest.raises(KeyError):
        resizer.get_width("unknown")


def test_set_width(resizer: ColumnResizer):
    resizer.set_width("age", 15)
    assert resizer.get_width("age") == 15


def test_set_width_clamped_to_max(resizer: ColumnResizer):
    resizer.set_width("name", 999)
    assert resizer.get_width("name") == resizer.max_width


def test_set_width_clamped_to_min(resizer: ColumnResizer):
    resizer.set_width("city", 1)
    assert resizer.get_width("city") == resizer.min_width


def test_widen(resizer: ColumnResizer):
    original = resizer.get_width("name")
    new_w = resizer.widen("name", step=3)
    assert new_w == original + 3


def test_narrow(resizer: ColumnResizer):
    original = resizer.get_width("name")
    new_w = resizer.narrow("name", step=2)
    assert new_w == original - 2


def test_widen_invalid_step_raises(resizer: ColumnResizer):
    with pytest.raises(ValueError, match="step"):
        resizer.widen("name", step=0)


def test_auto_fit(resizer: ColumnResizer):
    w = resizer.auto_fit("city", _SAMPLE_ROWS)
    # "Los Angeles" is 11 chars; clamped to max=40
    assert w == 11


def test_all_widths_returns_snapshot(resizer: ColumnResizer):
    snapshot = resizer.all_widths()
    assert set(snapshot.keys()) == {"name", "age", "city"}
    resizer.set_width("age", 20)
    assert snapshot["age"] == 10  # snapshot not mutated


def test_reset_restores_default(resizer: ColumnResizer):
    resizer.set_width("name", 30)
    resizer.reset(default_width=10)
    assert resizer.get_width("name") == 10


# ---------------------------------------------------------------------------
# ColumnResizeRenderer
# ---------------------------------------------------------------------------

def test_invalid_resizer_type_raises():
    with pytest.raises(TypeError):
        ColumnResizeRenderer("not-a-resizer")  # type: ignore[arg-type]


def test_render_header_length(renderer: ColumnResizeRenderer, resizer: ColumnResizer):
    line = renderer.render_header()
    # 3 cols × 10 chars + 2 separators " | " (3 chars each)
    expected_len = 3 * 10 + 2 * 3
    assert len(line) == expected_len


def test_render_header_contains_columns(renderer: ColumnResizeRenderer):
    line = renderer.render_header()
    for col in ["name", "age", "city"]:
        assert col in line


def test_render_row_truncates_long_value(
    resizer: ColumnResizer, renderer: ColumnResizeRenderer
):
    resizer.set_width("city", 6)
    row = {"name": "Alice", "age": "30", "city": "Los Angeles"}
    rendered = renderer.render_row(row)
    city_cell = rendered.split(" | ")[2]
    assert len(city_cell) == 6
    assert city_cell.endswith("…")


def test_render_divider_uses_dashes(renderer: ColumnResizeRenderer):
    divider = renderer.render_divider()
    for segment in divider.split(" | "):
        assert set(segment) == {"-"}


def test_render_table_includes_header(renderer: ColumnResizeRenderer):
    table = renderer.render_table(_SAMPLE_ROWS)
    lines = table.splitlines()
    assert "name" in lines[0]
    assert set(lines[1].replace(" | ", "").replace("-", "")) == set()  # divider


def test_render_table_row_count(renderer: ColumnResizeRenderer):
    table = renderer.render_table(_SAMPLE_ROWS)
    lines = table.splitlines()
    # header + divider + 3 data rows
    assert len(lines) == 5


def test_render_table_no_header(renderer: ColumnResizeRenderer):
    table = renderer.render_table(_SAMPLE_ROWS, include_header=False)
    lines = table.splitlines()
    assert len(lines) == 3


def test_render_visible_columns_subset(renderer: ColumnResizeRenderer):
    line = renderer.render_header(visible_columns=["name", "city"])
    assert "age" not in line
    assert "name" in line
    assert "city" in line
