"""Tests for ColumnStats and StatsReporter."""

import io
import pytest
from csvlens.column_stats import ColumnStats
from csvlens.stats_reporter import StatsReporter
from csvlens.csv_loader import CSVLoader


# ---------------------------------------------------------------------------
# ColumnStats unit tests
# ---------------------------------------------------------------------------

def test_numeric_column():
    stats = ColumnStats("age", ["25", "30", "22", "", "30"])
    assert stats.is_numeric is True
    assert stats.total_count == 5
    assert stats.null_count == 1
    assert stats.unique_count == 3
    assert stats.min_value == 22.0
    assert stats.max_value == 30.0
    assert stats.mean == pytest.approx((25 + 30 + 22 + 30) / 4)


def test_string_column():
    stats = ColumnStats("city", ["Paris", "London", "Paris", "Berlin"])
    assert stats.is_numeric is False
    assert stats.null_count == 0
    assert stats.unique_count == 3
    assert stats.mean is None
    assert stats.min_value == "Berlin"
    assert stats.max_value == "Paris"


def test_all_nulls_column():
    stats = ColumnStats("empty", ["", "", ""])
    assert stats.null_count == 3
    assert stats.unique_count == 0
    assert stats.is_numeric is False
    assert stats.min_value is None
    assert stats.max_value is None
    assert stats.mean is None


def test_top_values():
    stats = ColumnStats("color", ["red", "blue", "red", "green", "red", "blue"])
    top = dict(stats.top_values)
    assert top["red"] == 3
    assert top["blue"] == 2
    assert top["green"] == 1


def test_summary_keys():
    stats = ColumnStats("score", ["10", "20", "30"])
    summary = stats.summary()
    for key in ("name", "total", "nulls", "unique", "is_numeric", "min", "max", "top_values", "mean"):
        assert key in summary


# ---------------------------------------------------------------------------
# StatsReporter integration tests
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_text("name,age,city\nAlice,30,Paris\nBob,25,London\nCarol,30,Paris\n")
    return str(path)


def test_reporter_builds_stats(sample_csv):
    loader = CSVLoader(sample_csv)
    reporter = StatsReporter(loader)
    assert set(reporter.stats.keys()) == {"name", "age", "city"}


def test_reporter_get_existing_column(sample_csv):
    loader = CSVLoader(sample_csv)
    reporter = StatsReporter(loader)
    age_stats = reporter.get("age")
    assert age_stats is not None
    assert age_stats.is_numeric is True
    assert age_stats.mean == pytest.approx((30 + 25 + 30) / 3)


def test_reporter_get_missing_column(sample_csv):
    loader = CSVLoader(sample_csv)
    reporter = StatsReporter(loader)
    assert reporter.get("nonexistent") is None


def test_reporter_print_summary_no_error(sample_csv, capsys):
    loader = CSVLoader(sample_csv)
    reporter = StatsReporter(loader)
    reporter.print_summary()
    captured = capsys.readouterr()
    assert "name" in captured.out
    assert "age" in captured.out
    assert "city" in captured.out
