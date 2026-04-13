"""Tests for ExportEngine."""

import csv
import json
import io
import pytest

from csvlens.export_engine import ExportEngine


HEADERS = ["name", "age", "city"]

ROWS = [
    {"name": "Alice", "age": "30", "city": "NYC"},
    {"name": "Bob", "age": "25", "city": "LA"},
    {"name": "Carol", "age": "", "city": "Chicago"},
]


@pytest.fixture
def engine():
    return ExportEngine(HEADERS)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="Headers must not be empty"):
        ExportEngine([])


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_to_csv_all_columns(engine):
    result = engine.to_csv(ROWS)
    reader = csv.DictReader(io.StringIO(result))
    parsed = list(reader)
    assert len(parsed) == 3
    assert parsed[0]["name"] == "Alice"
    assert parsed[1]["city"] == "LA"


def test_to_csv_visible_columns(engine):
    result = engine.to_csv(ROWS, visible_columns=["name", "city"])
    reader = csv.DictReader(io.StringIO(result))
    parsed = list(reader)
    assert "age" not in parsed[0]
    assert parsed[0]["name"] == "Alice"


def test_to_json_all_columns(engine):
    result = engine.to_json(ROWS)
    parsed = json.loads(result)
    assert len(parsed) == 3
    assert parsed[0]["age"] == "30"


def test_to_json_visible_columns(engine):
    result = engine.to_json(ROWS, visible_columns=["name"])
    parsed = json.loads(result)
    assert list(parsed[0].keys()) == ["name"]


def test_export_dispatch_csv(engine):
    result = engine.export(ROWS, "csv")
    assert result.startswith("name,age,city")


def test_export_dispatch_json(engine):
    result = engine.export(ROWS, "json")
    parsed = json.loads(result)
    assert isinstance(parsed, list)


def test_export_unsupported_format_raises(engine):
    with pytest.raises(ValueError, match="Unsupported format"):
        engine.export(ROWS, "xml")


def test_export_unknown_column_raises(engine):
    with pytest.raises(ValueError, match="Unknown columns"):
        engine.to_csv(ROWS, visible_columns=["name", "salary"])


def test_to_csv_preserves_column_order(engine):
    result = engine.to_csv(ROWS, visible_columns=["city", "name"])
    header_line = result.splitlines()[0]
    assert header_line == "city,name"


def test_empty_rows_produces_header_only(engine):
    result = engine.to_csv([])
    assert result.strip() == "name,age,city"
