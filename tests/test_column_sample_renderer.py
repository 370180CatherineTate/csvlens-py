import pytest
from csvlens.column_sample_engine import ColumnSampleEngine
from csvlens.column_sample_renderer import ColumnSampleRenderer


HEADERS = ["product", "price", "stock"]
ROWS = [
    {"product": "Apple", "price": "1.20", "stock": "100"},
    {"product": "Banana", "price": "0.50", "stock": "200"},
    {"product": "Cherry", "price": "3.00", "stock": "50"},
]


@pytest.fixture
def engine():
    return ColumnSampleEngine(HEADERS, ROWS, sample_size=2, seed=0)


@pytest.fixture
def renderer(engine):
    return ColumnSampleRenderer(engine, col_width=12)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width must be at least 4"):
        ColumnSampleRenderer(engine, col_width=3)


def test_col_width_property(renderer):
    assert renderer.col_width == 12


def test_render_header_returns_string(renderer):
    header = renderer.render_header()
    assert isinstance(header, str)


def test_render_header_contains_columns(renderer):
    header = renderer.render_header()
    for col in HEADERS:
        assert col in header


def test_render_row_returns_string(renderer):
    row = renderer.render_row(0)
    assert isinstance(row, str)


def test_render_row_out_of_range_gives_empty_cells(renderer):
    row = renderer.render_row(999)
    # All cells should be blank (padded)
    stripped = row.strip()
    assert stripped == ""


def test_render_returns_multiline_string(renderer):
    output = renderer.render()
    lines = output.splitlines()
    # header + separator + sample_size rows
    assert len(lines) >= 3


def test_render_contains_separator(renderer):
    output = renderer.render()
    assert "---" in output


def test_fit_truncates_long_values():
    long_headers = ["a_very_long_column_name"]
    long_rows = [{"a_very_long_column_name": "some_value"} for _ in range(3)]
    eng = ColumnSampleEngine(long_headers, long_rows, sample_size=2, seed=0)
    rend = ColumnSampleRenderer(eng, col_width=8)
    header = rend.render_header()
    # Each cell must be exactly col_width characters
    assert len(header.split("  ")[0]) == 8
