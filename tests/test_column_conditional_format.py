"""Tests for ColumnConditionalFormat and ConditionalFormatRenderer."""
import pytest

from csvlens.column_conditional_format import ColumnConditionalFormat, ConditionalRule
from csvlens.conditional_format_renderer import ConditionalFormatRenderer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fmt():
    return ColumnConditionalFormat(["name", "score", "age"])


@pytest.fixture
def renderer(fmt):
    return ConditionalFormatRenderer(fmt, col_width=10)


# ---------------------------------------------------------------------------
# ColumnConditionalFormat
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnConditionalFormat([])


def test_headers_property(fmt):
    assert fmt.headers == ["name", "score", "age"]


def test_headers_returns_copy(fmt):
    h = fmt.headers
    h.append("extra")
    assert "extra" not in fmt.headers


def test_add_rule_invalid_column(fmt):
    with pytest.raises(KeyError):
        fmt.add_rule("missing", ">", 50.0, "red")


def test_add_rule_invalid_operator(fmt):
    with pytest.raises(ValueError, match="operator"):
        fmt.add_rule("score", "!!", 50.0, "red")


def test_add_rule_invalid_colour(fmt):
    with pytest.raises(ValueError, match="colour"):
        fmt.add_rule("score", ">", 50.0, "purple")


def test_rules_for_returns_copy(fmt):
    fmt.add_rule("score", ">", 80.0, "green")
    rules = fmt.rules_for("score")
    rules.clear()
    assert len(fmt.rules_for("score")) == 1


def test_clear_rules(fmt):
    fmt.add_rule("score", ">", 80.0, "green")
    fmt.clear_rules("score")
    assert fmt.rules_for("score") == []


def test_format_cell_no_rules(fmt):
    assert fmt.format_cell("score", "42") == "42"


def test_format_cell_matching_rule(fmt):
    fmt.add_rule("score", ">", 80.0, "green")
    result = fmt.format_cell("score", "95")
    assert "95" in result
    assert "\033[" in result  # ANSI code present


def test_format_cell_non_matching_rule(fmt):
    fmt.add_rule("score", ">", 80.0, "green")
    result = fmt.format_cell("score", "50")
    assert result == "50"  # no colour applied


def test_format_cell_non_numeric_unchanged(fmt):
    fmt.add_rule("name", ">", 0.0, "red")
    assert fmt.format_cell("name", "Alice") == "Alice"


def test_format_cell_unknown_column_returns_raw(fmt):
    assert fmt.format_cell("unknown", "99") == "99"


def test_conditional_rule_matches():
    rule = ConditionalRule("<=", 10.0, "red")
    assert rule.matches(10.0) is True
    assert rule.matches(11.0) is False


# ---------------------------------------------------------------------------
# ConditionalFormatRenderer
# ---------------------------------------------------------------------------

def test_invalid_col_width_raises(fmt):
    with pytest.raises(ValueError, match="col_width"):
        ConditionalFormatRenderer(fmt, col_width=0)


def test_col_width_property(renderer):
    assert renderer.col_width == 10


def test_render_header_returns_string(renderer):
    header = renderer.render_header()
    assert isinstance(header, str)
    assert "score" in header


def test_render_row_returns_string(fmt, renderer):
    row = {"name": "Alice", "score": "95", "age": "30"}
    result = renderer.render_row(row)
    assert isinstance(result, str)
    assert "Alice" in result


def test_render_all_contains_header_and_rows(fmt, renderer):
    rows = [
        {"name": "Alice", "score": "95", "age": "30"},
        {"name": "Bob",   "score": "40", "age": "25"},
    ]
    output = renderer.render_all(rows)
    assert "score" in output
    assert "Alice" in output
    assert "Bob" in output


def test_render_row_applies_colour(fmt, renderer):
    fmt.add_rule("score", ">", 80.0, "green")
    row = {"name": "Alice", "score": "95", "age": "30"}
    result = renderer.render_row(row)
    assert "\033[" in result
