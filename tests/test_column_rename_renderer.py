import pytest
from csvlens.column_rename_engine import ColumnRenameEngine
from csvlens.column_rename_renderer import ColumnRenameRenderer


@pytest.fixture
def engine():
    e = ColumnRenameEngine(["id", "name", "score"])
    e.set_rename("name", "Full Name")
    e.set_rename("score", "Score (%)")
    return e


@pytest.fixture
def renderer(engine):
    return ColumnRenameRenderer(engine, col_width=15)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError):
        ColumnRenameRenderer(engine, col_width=2)


def test_col_width_property(renderer):
    assert renderer.col_width == 15


def test_render_returns_string(renderer):
    assert isinstance(renderer.render(), str)


def test_render_contains_original(renderer):
    out = renderer.render()
    assert "name" in out
    assert "score" in out


def test_render_contains_display(renderer):
    out = renderer.render()
    assert "Full Name" in out
    assert "Score (%)" in out


def test_render_no_renames():
    e = ColumnRenameEngine(["a", "b"])
    r = ColumnRenameRenderer(e)
    assert "no renames" in r.render()


def test_render_row(engine):
    r = ColumnRenameRenderer(engine)
    row = {"id": "1", "name": "Alice", "score": "99"}
    result = r.render_row(row)
    assert result["Full Name"] == "Alice"
    assert result["Score (%)"] == "99"
    assert result["id"] == "1"


def test_render_row_missing_value(engine):
    r = ColumnRenameRenderer(engine)
    row = {"id": "7"}
    result = r.render_row(row)
    assert result["Full Name"] == ""
