"""Tests for the Paginator class."""

import pytest
from csvlens.pagination import Paginator


@pytest.fixture
def sample_rows():
    return [{"id": str(i), "value": f"val_{i}"} for i in range(55)]


@pytest.fixture
def paginator(sample_rows):
    return Paginator(sample_rows, page_size=10)


def test_total_rows(paginator):
    assert paginator.total_rows == 55


def test_total_pages(paginator):
    assert paginator.total_pages == 6


def test_page_size(paginator):
    assert paginator.page_size == 10


def test_get_first_page(paginator):
    page = paginator.get_page(0)
    assert len(page) == 10
    assert page[0]["id"] == "0"
    assert page[-1]["id"] == "9"


def test_get_last_page(paginator):
    page = paginator.get_page(5)
    assert len(page) == 5  # 55 % 10 == 5 remaining rows
    assert page[0]["id"] == "50"


def test_next_page(paginator):
    paginator.get_page(0)
    page = paginator.next_page()
    assert paginator.current_page == 1
    assert page[0]["id"] == "10"


def test_prev_page(paginator):
    paginator.get_page(3)
    page = paginator.prev_page()
    assert paginator.current_page == 2
    assert page[0]["id"] == "20"


def test_next_page_raises_on_last(paginator):
    paginator.get_page(5)
    with pytest.raises(IndexError):
        paginator.next_page()


def test_prev_page_raises_on_first(paginator):
    paginator.get_page(0)
    with pytest.raises(IndexError):
        paginator.prev_page()


def test_out_of_range_page(paginator):
    with pytest.raises(IndexError):
        paginator.get_page(99)


def test_negative_page_raises(paginator):
    with pytest.raises(IndexError):
        paginator.get_page(-1)


def test_invalid_page_size():
    with pytest.raises(ValueError):
        Paginator([], page_size=0)


def test_empty_rows():
    p = Paginator([], page_size=10)
    assert p.total_rows == 0
    assert p.total_pages == 0
    assert p.get_page() == []


def test_reset(paginator):
    paginator.get_page(4)
    paginator.reset()
    assert paginator.current_page == 0


def test_is_first_page(paginator):
    paginator.get_page(0)
    assert paginator.is_first_page() is True
    paginator.next_page()
    assert paginator.is_first_page() is False


def test_is_last_page(paginator):
    paginator.get_page(5)
    assert paginator.is_last_page() is True
    paginator.prev_page()
    assert paginator.is_last_page() is False
