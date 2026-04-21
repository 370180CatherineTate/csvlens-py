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
    # a <- b <- c  means c transitively depends on a
    engine.add_dependency("b", "a")
    engine.add_dependency("c", "b")
    assert "a" in engine.transitive_dependencies("c")
    assert "b" in engine.transitive_dependencies("c")


def test_transitive_dependencies_no_deps(engine: ColumnDependencyEngine) -> None:
    assert engine.transitive_dependencies("a") == []


def test_transitive_dependencies_direct_only(engine: ColumnDependencyEngine) -> None:
    engine.add_dependency("b", "a")
    assert engine.transitive_dependencies("b") == ["a"]


def test_transitive_dependencies_diamond(engine: ColumnDependencyEngine) -> None:
    # d depends on b and c; both b and c depend on a
    # transitive deps of d should include a exactly once
    engine.add_dependency("b", "a")
    engine.add_dependency("c", "a")
    engine.add_dependency("d", "b")
    engine.add_dependency("d", "c")
    transitive = engine.transitive_dependencies("d")
    assert transitive.count("a") == 1
    assert "b" in transitive
    assert "c" in transitive
