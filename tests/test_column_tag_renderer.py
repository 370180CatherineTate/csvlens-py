import pytest
from csvlens.column_tag_engine import ColumnTagEngine
from csvlens.column_tag_renderer import ColumnTagRenderer


@pytest.fixture
def engine():
    e = ColumnTagEngine(["name", "age", "email"])
    e.add_tag("name", "pii")
    e.add_tag("email", "pii")
    e.add_tag("age", "numeric")
    return e


@pytest.fixture
def renderer(engine):
    return ColumnTagRenderer(engine)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError):
        ColumnTagRenderer(engine, col_width=3)


def test_col_width_property(renderer):
    assert renderer.col_width == 18


def test_render_returns_string(renderer):
    assert isinstance(renderer.render(), str)


def test_render_contains_column_header(renderer):
    out = renderer.render()
    assert "Column" in out


def test_render_contains_column_names(renderer):
    out = renderer.render()
    for col in ["name", "age", "email"]:
        assert col in out


def test_render_contains_tags(renderer):
    out = renderer.render()
    assert "pii" in out
    assert "numeric" in out


def test_render_none_tag_shown(engine):
    e = ColumnTagEngine(["score"])
    r = ColumnTagRenderer(e)
    assert "(none)" in r.render()
