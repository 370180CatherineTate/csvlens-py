"""Tests for csvlens.csv_loader.CSVLoader."""

import csv
import pytest
from pathlib import Path

from csvlens.csv_loader import CSVLoader


@pytest.fixture()
def simple_csv(tmp_path: Path) -> Path:
    """Create a small CSV file for testing."""
    filepath = tmp_path / "sample.csv"
    rows = [
        ["name", "age", "city"],
        ["Alice", "30", "New York"],
        ["Bob", "25", "London"],
        ["Charlie", "35", "Paris"],
    ]
    with filepath.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return filepath


@pytest.fixture()
def empty_csv(tmp_path: Path) -> Path:
    filepath = tmp_path / "empty.csv"
    filepath.write_text("")
    return filepath


def test_headers(simple_csv: Path):
    loader = CSVLoader(str(simple_csv))
    assert loader.headers == ["name", "age", "city"]


def test_row_count(simple_csv: Path):
    loader = CSVLoader(str(simple_csv))
    assert loader.row_count == 3


def test_column_count(simple_csv: Path):
    loader = CSVLoader(str(simple_csv))
    assert loader.column_count == 3


def test_iter_rows(simple_csv: Path):
    loader = CSVLoader(str(simple_csv))
    rows = list(loader.iter_rows())
    assert len(rows) == 3
    assert rows[0] == {"name": "Alice", "age": "30", "city": "New York"}
    assert rows[2]["name"] == "Charlie"


def test_load_rows_no_limit(simple_csv: Path):
    loader = CSVLoader(str(simple_csv))
    rows = loader.load_rows()
    assert len(rows) == 3


def test_load_rows_with_limit(simple_csv: Path):
    loader = CSVLoader(str(simple_csv))
    rows = loader.load_rows(limit=2)
    assert len(rows) == 2
    assert rows[-1]["name"] == "Bob"


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        CSVLoader("/nonexistent/path/file.csv")


def test_empty_file_raises(empty_csv: Path):
    with pytest.raises(ValueError, match="empty"):
        CSVLoader(str(empty_csv))


def test_repr(simple_csv: Path):
    loader = CSVLoader(str(simple_csv))
    r = repr(loader)
    assert "CSVLoader" in r
    assert "columns=3" in r
    assert "rows=3" in r
