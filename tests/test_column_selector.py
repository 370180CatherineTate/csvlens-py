"""Tests for the ColumnSelector module."""

import pytest
from csvlens.column_selector import ColumnSelector


HEADERS = ["name", "age", "city", "score"]


@pytest.fixture
def selector() -> ColumnSelector:
    return ColumnSelector(HEADERS)


def test_init_all_visible(selector: ColumnSelector) -> None:
    assert selector.visible_headers == HEADERS


def test_headers_returns_all(selector: ColumnSelector) -> None:
    assert selector.headers == HEADERS


def test_empty_headers_raises() -> None:
    with pytest.raises(ValueError):
        ColumnSelector([])


def test_hide_column(selector: ColumnSelector) -> None:
    selector.hide("age")
    assert "age" not in selector.visible_headers
    assert "age" in selector.hidden_headers


def test_show_column(selector: ColumnSelector) -> None:
    selector.hide("city")
    selector.show("city")
    assert "city" in selector.visible_headers
    assert "city" not in selector.hidden_headers


def test_toggle_hides_visible(selector: ColumnSelector) -> None:
    result = selector.toggle("name")
    assert result is False
    assert "name" not in selector.visible_headers


def test_toggle_shows_hidden(selector: ColumnSelector) -> None:
    selector.hide("score")
    result = selector.toggle("score")
    assert result is True
    assert "score" in selector.visible_headers


def test_is_visible(selector: ColumnSelector) -> None:
    assert selector.is_visible("name") is True
    selector.hide("name")
    assert selector.is_visible("name") is False


def test_hide_all(selector: ColumnSelector) -> None:
    selector.hide_all()
    assert selector.visible_headers == []
    assert selector.hidden_headers == HEADERS


def test_show_all(selector: ColumnSelector) -> None:
    selector.hide_all()
    selector.show_all()
    assert selector.visible_headers == HEADERS


def test_visible_order_preserved(selector: ColumnSelector) -> None:
    selector.hide("age")
    assert selector.visible_headers == ["name", "city", "score"]


def test_hide_nonexistent_raises(selector: ColumnSelector) -> None:
    with pytest.raises(KeyError):
        selector.hide("nonexistent")


def test_show_nonexistent_raises(selector: ColumnSelector) -> None:
    with pytest.raises(KeyError):
        selector.show("nonexistent")


def test_toggle_nonexistent_raises(selector: ColumnSelector) -> None:
    with pytest.raises(KeyError):
        selector.toggle("nonexistent")


def test_filter_row(selector: ColumnSelector) -> None:
    selector.hide("age")
    row = {"name": "Alice", "age": "30", "city": "NY", "score": "95"}
    filtered = selector.filter_row(row)
    assert filtered == {"name": "Alice", "city": "NY", "score": "95"}
    assert "age" not in filtered


def test_filter_row_all_hidden(selector: ColumnSelector) -> None:
    selector.hide_all()
    row = {"name": "Bob", "age": "25", "city": "LA", "score": "80"}
    assert selector.filter_row(row) == {}
