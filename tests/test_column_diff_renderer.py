import pytest
from csvlens.column_diff_profile import ColumnDiffProfile
from csvlens.column_diff_renderer import ColumnDiffRenderer

HEADERS = ["name", "score", "status"]
ROWS_A = [
    {"name": "Alice", "score": "10", "status": "ok"},
    {"name": "Bob", "score": "20", "status": "ok"},
]
ROWS_B = [
    {"name": "Alice", "score": "15", "status": "ok"},
    {"name": "Bob", "score": "20", "status": "fail"},
]


@pytest.fixture
def profile():
    p = ColumnDiffProfile(HEADERS)
    p.save_snapshot("before", ROWS_A)
    p.save_snapshot("after", ROWS_B)
    return p


@pytest.fixture
def renderer(profile):
    return ColumnDiffRenderer(profile)


def test_invalid_col_width_raises(profile):
    with pytest.raises(ValueError):
        ColumnDiffRenderer(profile, col_width=3)


def test_col_width_property(renderer):
    assert renderer.col_width == 18


def test_render_returns_string(renderer):
    out = renderer.render("before", "after")
    assert isinstance(out, str)


def test_render_contains_all_columns(renderer):
    out = renderer.render("before", "after")
    for h in HEADERS:
        assert h in out


def test_render_shows_diff_counts(renderer):
    out = renderer.render("before", "after")
    assert "1" in out


def test_render_missing_snapshot_raises(renderer):
    with pytest.raises(KeyError):
        renderer.render("before", "ghost")


def test_render_has_header_line(renderer):
    out = renderer.render("before", "after")
    assert "Column" in out
    assert "Changed Rows" in out
