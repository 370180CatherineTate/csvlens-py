"""Tests for ColumnDependencyEngine and ColumnDependencyRenderer."""
import pytest

from csvlens.column_dependency_engine import ColumnDependencyEngine
from csvlens.column_dependency_renderer import ColumnDependencyRenderer


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def engine() -> ColumnDependencyEngine:
    return ColumnDependencyEngine(["a", "b", "c", "d"])


@pytest.fixture()
def renderer(engine: ColumnDependencyEngine) -> ColumnDependencyRenderer:
    return ColumnDependencyRenderer(engine, col_width=20)


# ---------------------------------------------------------------------------
# ColumnDependencyEngine – construction
# ---------------------------------------------------------------------------

def test_empty_headers_raises() -> None:
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnDependencyEngine([])


def test_headers_property(engine: ColumnDependencyEngine) -> None:
    assert engine.headers == ["a", "b", "c", "d"]


def test_headers_returns_copy(engine: ColumnDependencyEngine) -> None:
    h = engine.headers
    h.append("z")
    assert "z" not in engine.headers


def test_initial_no_dependencies(engine: ColumnDependencyEngine) -> None:
    for col in engine.headers:
        assert engine.direct_dependencies(col) == []


# ---------------------------------------------------------------------------
# add / remove / clear
# ---------------------------------------------------------------------------

def test_add_dependency(engine: ColumnDependencyEngine) -> None:
    engine.add_dependency("b", "a")
    assert "a" in engine.direct_dependencies("b")


def test_add_dependency_unknown_column_raises(engine: ColumnDependencyEngine) -> None:
    with pytest.raises(KeyError):
        engine.add_dependency("b", "z")


def test_add_self_dependency_raises(engine: ColumnDependencyEngine) -> None:
    with pytest.raises(ValueError, match="cannot depend on itself"):
        engine.add_dependency("a", "a")


def test_remove_dependency(engine: ColumnDependencyEngine) -> None:
    engine.add_dependency("b", "a")
    engine.remove_dependency("b", "a")
    assert engine.direct_dependencies("b") == []


def test_remove_nonexistent_is_noop(engine: ColumnDependencyEngine) -> None:
    engine.remove_dependency("b", "a")  # should not raise
    assert engine.direct_dependencies("b") == []


def test_clear_dependencies(engine: ColumnDependencyEngine) -> None:
    engine.add_dependency("c", "a")
    engine.add_dependency("c", "b")
    engine.clear_dependencies("c")
    assert engine.direct_dependencies("c") == []


# ---------------------------------------------------------------------------
# transitive dependencies
# ---------------------------------------------------------------------------

def test_transitive_dependencies_simple(engine: ColumnDependencyEngine) -> None:
    engine.add_dependency("b", "a")
    engine.add_dependency("c", "b")
    trans = engine.transitive_dependencies("c")
    assert "a" in trans
    assert "b" in trans


def test_transitive_no_cycle_infinite_loop(engine: ColumnDependencyEngine) -> None:
    # Even if data were cyclic (shouldn't happen via public API), visited guard
    # prevents infinite loop – test that transitive terminates.
    engine.add_dependency("b", "a")
    result = engine.transitive_dependencies("b")
    assert result == ["a"]


# ---------------------------------------------------------------------------
# dependents
# ---------------------------------------------------------------------------

def test_dependents(engine: ColumnDependencyEngine) -> None:
    engine.add_dependency("b", "a")
    engine.add_dependency("c", "a")
    deps = engine.dependents("a")
    assert "b" in deps
    assert "c" in deps


def test_dependents_unknown_column_raises(engine: ColumnDependencyEngine) -> None:
    with pytest.raises(KeyError):
        engine.dependents("z")


# ---------------------------------------------------------------------------
# ColumnDependencyRenderer
# ---------------------------------------------------------------------------

def test_invalid_col_width_raises(engine: ColumnDependencyEngine) -> None:
    with pytest.raises(ValueError, match="col_width"):
        ColumnDependencyRenderer(engine, col_width=3)


def test_col_width_property(renderer: ColumnDependencyRenderer) -> None:
    assert renderer.col_width == 20


def test_render_returns_string(
    engine: ColumnDependencyEngine, renderer: ColumnDependencyRenderer
) -> None:
    result = renderer.render("a")
    assert isinstance(result, str)


def test_render_contains_column_name(
    engine: ColumnDependencyEngine, renderer: ColumnDependencyRenderer
) -> None:
    result = renderer.render("b")
    assert "b" in result


def test_render_shows_none_when_no_deps(
    engine: ColumnDependencyEngine, renderer: ColumnDependencyRenderer
) -> None:
    result = renderer.render("a")
    assert "(none)" in result


def test_render_transitive_flag(
    engine: ColumnDependencyEngine, renderer: ColumnDependencyRenderer
) -> None:
    engine.add_dependency("b", "a")
    engine.add_dependency("c", "b")
    result = renderer.render("c", transitive=True)
    assert "Trans. Deps" in result
    assert "a" in result
