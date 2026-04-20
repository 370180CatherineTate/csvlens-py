import pytest

from csvlens.column_validation_engine import (
    ColumnValidationEngine,
    ValidationRule,
)
from csvlens.column_validation_renderer import ColumnValidationRenderer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def engine():
    return ColumnValidationEngine(["name", "age", "email"])


@pytest.fixture
def renderer(engine):
    return ColumnValidationRenderer(engine, col_width=12)


# ---------------------------------------------------------------------------
# ValidationRule tests
# ---------------------------------------------------------------------------

def test_invalid_rule_type_raises():
    with pytest.raises(ValueError):
        ValidationRule("unknown")


def test_regex_without_param_raises():
    with pytest.raises(ValueError):
        ValidationRule("regex")


def test_max_len_without_param_raises():
    with pytest.raises(ValueError):
        ValidationRule("max_len")


def test_not_empty_passes():
    rule = ValidationRule("not_empty")
    assert rule.check("hello") is True


def test_not_empty_fails():
    rule = ValidationRule("not_empty")
    assert rule.check("") is False
    assert rule.check("   ") is False


def test_numeric_passes():
    rule = ValidationRule("numeric")
    assert rule.check("3.14") is True
    assert rule.check("-7") is True


def test_numeric_fails():
    rule = ValidationRule("numeric")
    assert rule.check("abc") is False


def test_regex_passes():
    rule = ValidationRule("regex", r"^\d{3}$")
    assert rule.check("123") is True


def test_regex_fails():
    rule = ValidationRule("regex", r"^\d{3}$")
    assert rule.check("12") is False


def test_max_len_passes():
    rule = ValidationRule("max_len", "5")
    assert rule.check("hello") is True


def test_max_len_fails():
    rule = ValidationRule("max_len", "3")
    assert rule.check("toolong") is False


# ---------------------------------------------------------------------------
# ColumnValidationEngine tests
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnValidationEngine([])


def test_headers_property(engine):
    assert engine.headers == ["name", "age", "email"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_initial_no_rules(engine):
    assert engine.rules == {}


def test_add_rule_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.add_rule("nonexistent", ValidationRule("not_empty"))


def test_add_rule_stores_rule(engine):
    engine.add_rule("age", ValidationRule("numeric"))
    assert len(engine.rules["age"]) == 1


def test_clear_rules_removes(engine):
    engine.add_rule("age", ValidationRule("numeric"))
    engine.clear_rules("age")
    assert "age" not in engine.rules


def test_clear_rules_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.clear_rules("ghost")


def test_validate_row_no_errors(engine):
    engine.add_rule("age", ValidationRule("numeric"))
    result = engine.validate_row({"name": "Alice", "age": "30", "email": "a@b.com"})
    assert result == {}


def test_validate_row_with_error(engine):
    engine.add_rule("age", ValidationRule("numeric"))
    result = engine.validate_row({"name": "Bob", "age": "old", "email": "b@c.com"})
    assert "age" in result
    assert "numeric" in result["age"]


def test_validate_rows_filters_valid(engine):
    engine.add_rule("age", ValidationRule("numeric"))
    rows = [
        {"name": "Alice", "age": "25", "email": "a@b.com"},
        {"name": "Bob", "age": "NaN", "email": "b@c.com"},
    ]
    bad = engine.validate_rows(rows)
    assert len(bad) == 1
    assert bad[0][0] == 1


# ---------------------------------------------------------------------------
# ColumnValidationRenderer tests
# ---------------------------------------------------------------------------

def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError):
        ColumnValidationRenderer(engine, col_width=3)


def test_col_width_property(renderer):
    assert renderer.col_width == 12


def test_render_header_returns_string(renderer):
    result = renderer.render_header()
    assert isinstance(result, str)
    assert "name" in result
    assert "age" in result


def test_render_row_no_errors(renderer):
    row = {"name": "Alice", "age": "30", "email": "a@b.com"}
    result = renderer.render_row(row, {})
    assert "Alice" in result


def test_render_row_marks_error_column(renderer, engine):
    engine.add_rule("age", ValidationRule("numeric"))
    row = {"name": "Bob", "age": "old", "email": "b@c.com"}
    errors = engine.validate_row(row)
    result = renderer.render_row(row, errors)
    # ANSI red code should appear
    assert "\033[31m" in result


def test_render_summary_all_valid(renderer):
    result = renderer.render_summary([])
    assert "valid" in result.lower()


def test_render_summary_with_errors(renderer, engine):
    engine.add_rule("age", ValidationRule("numeric"))
    rows = [{"name": "X", "age": "bad", "email": ""}]
    bad = engine.validate_rows(rows)
    result = renderer.render_summary(bad)
    assert "age" in result
    assert "1" in result
