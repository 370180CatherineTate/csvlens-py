import pytest
from csvlens.column_pivot_engine import ColumnPivotEngine
from csvlens.column_pivot_renderer import ColumnPivotRenderer

HEADERS = ["category", "amount", "name"]
ROWS = [
    {"category": "A", "amount": "10", "name": "x"},
    {"category": "B", "amount": "20", "name": "y"},
    {"category": "A", "amount": "30", "name": "z"},
    {"category": "B", "amount": "bad", "name": "w"},
]


@pytest.fixture
def engine():
    return ColumnPivotEngine(HEADERS)


@pytest.fixture
def renderer(engine):
    engine.configure("category", "amount", "sum")
    return ColumnPivotRenderer(engine)


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnPivotEngine([])


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == HEADERS


def test_default_state(engine):
    assert engine.key_column is None
    assert engine.value_column is None
    assert engine.agg == "count"


def test_configure_valid(engine):
    engine.configure("category", "amount", "sum")
    assert engine.key_column == "category"
    assert engine.value_column == "amount"
    assert engine.agg == "sum"


def test_configure_invalid_key_raises(engine):
    with pytest.raises(ValueError, match="key_column"):
        engine.configure("missing", "amount")


def test_configure_invalid_value_raises(engine):
    with pytest.raises(ValueError, match="value_column"):
        engine.configure("category", "missing")


def test_configure_invalid_agg_raises(engine):
    with pytest.raises(ValueError, match="agg"):
        engine.configure("category", "amount", agg="median")


def test_pivot_without_configure_raises(engine):
    with pytest.raises(RuntimeError):
        engine.pivot(ROWS)


def test_pivot_sum(engine):
    engine.configure("category", "amount", "sum")
    result = engine.pivot(ROWS)
    assert result["A"] == 40.0
    assert result["B"] == 20.0  # 'bad' coerced to 0


def test_pivot_count(engine):
    engine.configure("category", "amount", "count")
    result = engine.pivot(ROWS)
    assert result["A"] == 2.0
    assert result["B"] == 2.0


def test_pivot_mean(engine):
    engine.configure("category", "amount", "mean")
    result = engine.pivot(ROWS)
    assert result["A"] == 20.0
    assert result["B"] == 10.0


def test_reset(engine):
    engine.configure("category", "amount", "mean")
    engine.reset()
    assert engine.key_column is None
    assert engine.agg == "count"


def test_renderer_invalid_col_width_raises(engine):
    engine.configure("category", "amount")
    with pytest.raises(ValueError):
        ColumnPivotRenderer(engine, col_width=2)


def test_renderer_col_width_property(renderer):
    assert renderer.col_width == 16


def test_renderer_render_returns_string(renderer):
    result = renderer.render({"A": 40.0, "B": 20.0})
    assert isinstance(result, str)


def test_renderer_render_contains_keys(renderer):
    result = renderer.render({"A": 40.0, "B": 20.0})
    assert "A" in result
    assert "B" in result


def test_renderer_empty_pivot(renderer):
    result = renderer.render({})
    assert "no data" in result
