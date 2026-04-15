"""Tests for ColumnFormulaEngine."""
import pytest
from csvlens.column_formula_engine import ColumnFormulaEngine


@pytest.fixture
def engine():
    return ColumnFormulaEngine(["name", "price", "qty"])


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnFormulaEngine([])


def test_headers_property(engine):
    assert engine.headers == ["name", "price", "qty"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_initial_no_formulas(engine):
    assert engine.formula_names == []
    assert engine.formulas == {}


def test_set_formula_registers(engine):
    engine.set_formula("total", "price * qty")
    assert "total" in engine.formula_names
    assert engine.formulas["total"] == "price * qty"


def test_set_formula_empty_name_raises(engine):
    with pytest.raises(ValueError):
        engine.set_formula("", "price * qty")


def test_set_formula_empty_expression_raises(engine):
    with pytest.raises(ValueError):
        engine.set_formula("total", "")


def test_set_formula_overwrites(engine):
    engine.set_formula("total", "price * qty")
    engine.set_formula("total", "price + qty")
    assert engine.formulas["total"] == "price + qty"


def test_remove_formula(engine):
    engine.set_formula("total", "price * qty")
    engine.remove_formula("total")
    assert "total" not in engine.formula_names


def test_remove_nonexistent_raises(engine):
    with pytest.raises(KeyError):
        engine.remove_formula("ghost")


def test_clear_removes_all(engine):
    engine.set_formula("a", "price")
    engine.set_formula("b", "qty")
    engine.clear()
    assert engine.formula_names == []


def test_evaluate_row_arithmetic(engine):
    engine.set_formula("total", "price * qty")
    row = {"name": "apple", "price": "3", "qty": "4"}
    assert engine.evaluate_row("total", row) == "12"


def test_evaluate_row_string_fallback(engine):
    engine.set_formula("label", "name")
    row = {"name": "apple", "price": "3", "qty": "4"}
    assert engine.evaluate_row("label", row) == "apple"


def test_evaluate_row_error_returns_none(engine):
    engine.set_formula("bad", "nonexistent_var + 1")
    row = {"name": "x", "price": "1", "qty": "2"}
    assert engine.evaluate_row("bad", row) is None


def test_evaluate_unknown_formula_raises(engine):
    with pytest.raises(KeyError):
        engine.evaluate_row("ghost", {})


def test_apply_appends_columns(engine):
    engine.set_formula("total", "price * qty")
    rows = [{"name": "a", "price": "2", "qty": "5"}]
    result = engine.apply(rows)
    assert result[0]["total"] == "10"
    assert "name" in result[0]


def test_apply_returns_new_list(engine):
    rows = [{"name": "a", "price": "2", "qty": "5"}]
    result = engine.apply(rows)
    assert result is not rows
