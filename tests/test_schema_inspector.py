"""Tests for SchemaInspector."""

import pytest
from csvlens.schema_inspector import SchemaInspector, _infer_cell_type


# ---------------------------------------------------------------------------
# _infer_cell_type unit tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    ("42", "integer"),
    ("-7", "integer"),
    ("3.14", "float"),
    (".5", "float"),
    ("-0.001", "float"),
    ("true", "boolean"),
    ("False", "boolean"),
    ("yes", "boolean"),
    ("2024-01-15", "date"),
    ("15/06/2023", "date"),
    ("hello", "string"),
    ("", "null"),
    ("  ", "null"),
])
def test_infer_cell_type(value, expected):
    assert _infer_cell_type(value) == expected


# ---------------------------------------------------------------------------
# SchemaInspector tests
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "name": "Alice", "score": "9.5", "active": "true", "dob": "1990-05-20"},
        {"id": "2", "name": "Bob",   "score": "7.0", "active": "false", "dob": "1985-11-03"},
        {"id": "3", "name": "Carol", "score": "8.2", "active": "yes",   "dob": "2000-01-01"},
    ]


@pytest.fixture
def inspector(sample_rows):
    headers = ["id", "name", "score", "active", "dob"]
    return SchemaInspector(headers, sample_rows)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        SchemaInspector([], [])


def test_headers_property(inspector):
    assert inspector.headers == ["id", "name", "score", "active", "dob"]


def test_schema_returns_dict(inspector):
    schema = inspector.schema
    assert isinstance(schema, dict)
    assert set(schema.keys()) == {"id", "name", "score", "active", "dob"}


def test_integer_column(inspector):
    assert inspector.type_of("id") == "integer"


def test_string_column(inspector):
    assert inspector.type_of("name") == "string"


def test_float_column(inspector):
    assert inspector.type_of("score") == "float"


def test_boolean_column(inspector):
    assert inspector.type_of("active") == "boolean"


def test_date_column(inspector):
    assert inspector.type_of("dob") == "date"


def test_type_of_unknown_column_returns_none(inspector):
    assert inspector.type_of("nonexistent") is None


def test_columns_of_type(inspector):
    floats = inspector.columns_of_type("float")
    assert floats == ["score"]


def test_all_nulls_column():
    headers = ["a"]
    rows = [{"a": ""}, {"a": ""}, {"a": ""}]
    ins = SchemaInspector(headers, rows)
    assert ins.type_of("a") == "null"


def test_no_sample_rows_defaults_to_null():
    ins = SchemaInspector(["x", "y"], [])
    assert ins.type_of("x") == "null"
    assert ins.type_of("y") == "null"


def test_schema_is_copy(inspector):
    s1 = inspector.schema
    s1["id"] = "tampered"
    assert inspector.type_of("id") == "integer"
