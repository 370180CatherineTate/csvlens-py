"""Tests for ColumnSearchHistory and SearchHistoryRenderer."""
import pytest
from csvlens.column_search_history import ColumnSearchHistory
from csvlens.search_history_renderer import SearchHistoryRenderer

HEADERS = ["name", "age", "city"]


@pytest.fixture
def history():
    return ColumnSearchHistory(HEADERS)


@pytest.fixture
def renderer(history):
    return SearchHistoryRenderer(history, col_width=30)


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnSearchHistory([])


def test_max_history_too_small_raises():
    with pytest.raises(ValueError):
        ColumnSearchHistory(HEADERS, max_history=0)


def test_headers_property(history):
    assert history.headers == HEADERS


def test_headers_returns_copy(history):
    h = history.headers
    h.append("extra")
    assert "extra" not in history.headers


def test_push_global_records_pattern(history):
    history.push_global("foo")
    assert history.global_history() == ["foo"]


def test_push_global_deduplicates_consecutive(history):
    history.push_global("foo")
    history.push_global("foo")
    assert history.global_history() == ["foo"]


def test_push_global_newest_first(history):
    history.push_global("first")
    history.push_global("second")
    assert history.global_history()[0] == "second"


def test_push_global_empty_raises(history):
    with pytest.raises(ValueError):
        history.push_global("")


def test_push_column_records_pattern(history):
    history.push_column("age", "30")
    assert history.column_history("age") == ["30"]


def test_push_column_unknown_raises(history):
    with pytest.raises(KeyError):
        history.push_column("unknown", "x")


def test_push_column_empty_raises(history):
    with pytest.raises(ValueError):
        history.push_column("name", "")


def test_column_history_unknown_raises(history):
    with pytest.raises(KeyError):
        history.column_history("nope")


def test_clear_global(history):
    history.push_global("a")
    history.clear_global()
    assert history.global_history() == []


def test_clear_column(history):
    history.push_column("city", "Paris")
    history.clear_column("city")
    assert history.column_history("city") == []


def test_clear_all(history):
    history.push_global("g")
    history.push_column("name", "Alice")
    history.clear_all()
    assert history.global_history() == []
    assert history.column_history("name") == []


def test_renderer_invalid_col_width_raises(history):
    with pytest.raises(ValueError):
        SearchHistoryRenderer(history, col_width=4)


def test_renderer_col_width_property(renderer):
    assert renderer.col_width == 30


def test_render_global_no_history(renderer):
    result = renderer.render()
    assert "no history" in result


def test_render_global_with_items(history, renderer):
    history.push_global("alpha")
    history.push_global("beta")
    result = renderer.render()
    assert "beta" in result
    assert "alpha" in result


def test_render_column_with_items(history, renderer):
    history.push_column("name", "Alice")
    result = renderer.render(column="name")
    assert "Alice" in result
    assert "[name]" in result


def test_render_column_no_history(renderer):
    result = renderer.render(column="age")
    assert "no history" in result
