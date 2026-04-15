"""Tests for ColumnColorEngine."""
import pytest
from csvlens.column_color_engine import ColumnColorEngine


@pytest.fixture
def engine():
    return ColumnColorEngine(["name", "age", "score", "email"])


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnColorEngine([])


def test_headers_property(engine):
    assert engine.headers == ["name", "age", "score", "email"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_set_color_exact(engine):
    engine.set_color("name", "red")
    assert engine.color_for("name") == "red"


def test_set_color_case_insensitive(engine):
    engine.set_color("age", "BLUE")
    assert engine.color_for("age") == "blue"


def test_set_color_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="Unknown column"):
        engine.set_color("missing", "red")


def test_set_color_invalid_color_raises(engine):
    with pytest.raises(ValueError, match="Invalid color"):
        engine.set_color("name", "purple")


def test_color_for_no_rule_returns_none(engine):
    assert engine.color_for("score") is None


def test_clear_color_removes_rule(engine):
    engine.set_color("name", "green")
    engine.clear_color("name")
    assert engine.color_for("name") is None


def test_clear_color_nonexistent_is_noop(engine):
    engine.clear_color("name")  # no error


def test_set_pattern_color_matches(engine):
    engine.set_pattern_color(r"e$", "cyan")  # name, score, age, email end in 'e'
    assert engine.color_for("name") == "cyan"
    assert engine.color_for("score") == "cyan"


def test_exact_overrides_pattern(engine):
    engine.set_pattern_color(r".*", "yellow")
    engine.set_color("name", "magenta")
    assert engine.color_for("name") == "magenta"
    assert engine.color_for("age") == "yellow"


def test_set_pattern_invalid_regex_raises(engine):
    with pytest.raises(Exception):
        engine.set_pattern_color("[unclosed", "red")


def test_ansi_for_returns_empty_when_no_color(engine):
    assert engine.ansi_for("name") == ""


def test_ansi_for_returns_code(engine):
    engine.set_color("name", "red")
    code = engine.ansi_for("name")
    assert "\033[" in code


def test_colorize_wraps_text(engine):
    engine.set_color("age", "green")
    result = engine.colorize("age", "42")
    assert "42" in result
    assert "\033[" in result
    assert "\033[0m" in result


def test_colorize_no_color_returns_plain(engine):
    assert engine.colorize("score", "99") == "99"


def test_clear_all(engine):
    engine.set_color("name", "red")
    engine.set_pattern_color(r".*", "blue")
    engine.clear_all()
    assert engine.color_for("name") is None
    assert engine.color_for("age") is None
