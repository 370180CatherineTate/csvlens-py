"""Tests for ScrollEngine."""
import pytest
from csvlens.scroll_engine import ScrollEngine


@pytest.fixture
def engine():
    """A ScrollEngine with 50 rows, 10 cols, page_size=10, col_window=3."""
    return ScrollEngine(total_rows=50, total_cols=10, page_size=10, col_window=3)


def test_negative_total_rows_raises():
    with pytest.raises(ValueError, match="total_rows"):
        ScrollEngine(total_rows=-1, total_cols=5)


def test_zero_total_cols_raises():
    with pytest.raises(ValueError, match="total_cols"):
        ScrollEngine(total_rows=10, total_cols=0)


def test_invalid_page_size_raises():
    with pytest.raises(ValueError, match="page_size"):
        ScrollEngine(total_rows=10, total_cols=5, page_size=0)


def test_invalid_col_window_raises():
    with pytest.raises(ValueError, match="col_window"):
        ScrollEngine(total_rows=10, total_cols=5, col_window=-1)


def test_initial_offsets_are_zero(engine):
    assert engine.row_offset == 0
    assert engine.col_offset == 0


def test_max_row_offset(engine):
    assert engine.max_row_offset == 40  # 50 - 10


def test_max_col_offset(engine):
    assert engine.max_col_offset == 7  # 10 - 3


def test_scroll_down_basic(engine):
    engine.scroll_down(5)
    assert engine.row_offset == 5


def test_scroll_down_clamps_at_max(engine):
    engine.scroll_down(100)
    assert engine.row_offset == engine.max_row_offset


def test_scroll_up_from_zero_stays_at_zero(engine):
    engine.scroll_up(3)
    assert engine.row_offset == 0


def test_scroll_up_after_down(engine):
    engine.scroll_down(10)
    engine.scroll_up(4)
    assert engine.row_offset == 6


def test_scroll_right_basic(engine):
    engine.scroll_right(2)
    assert engine.col_offset == 2


def test_scroll_right_clamps_at_max(engine):
    engine.scroll_right(50)
    assert engine.col_offset == engine.max_col_offset


def test_scroll_left_from_zero_stays_at_zero(engine):
    engine.scroll_left(1)
    assert engine.col_offset == 0


def test_scroll_left_after_right(engine):
    engine.scroll_right(5)
    engine.scroll_left(2)
    assert engine.col_offset == 3


def test_jump_to_row_valid(engine):
    engine.jump_to_row(20)
    assert engine.row_offset == 20


def test_jump_to_row_clamps_negative(engine):
    engine.jump_to_row(-5)
    assert engine.row_offset == 0


def test_jump_to_row_clamps_beyond_max(engine):
    engine.jump_to_row(999)
    assert engine.row_offset == engine.max_row_offset


def test_reset_restores_origin(engine):
    engine.scroll_down(15)
    engine.scroll_right(4)
    engine.reset()
    assert engine.row_offset == 0
    assert engine.col_offset == 0


def test_visible_row_slice(engine):
    engine.scroll_down(5)
    s = engine.visible_row_slice()
    assert s == slice(5, 15)


def test_visible_col_slice(engine):
    engine.scroll_right(2)
    s = engine.visible_col_slice()
    assert s == slice(2, 5)


def test_zero_total_rows_allowed():
    eng = ScrollEngine(total_rows=0, total_cols=3, page_size=10, col_window=3)
    assert eng.max_row_offset == 0
    eng.scroll_down(1)
    assert eng.row_offset == 0
