"""Tests for ColumnSparkline and SparklineRenderer."""
import pytest

from csvlens.column_sparkline import ColumnSparkline, _to_buckets
from csvlens.sparkline_renderer import SparklineRenderer


HEADERS = ["name", "age", "score"]
ROWS = [
    {"name": "Alice", "age": "30", "score": "88.5"},
    {"name": "Bob", "age": "25", "score": "72.0"},
    {"name": "Carol", "age": "35", "score": "95.0"},
    {"name": "Dave", "age": "", "score": "60.0"},
    {"name": "Eve", "age": "28", "score": "72.0"},
]


@pytest.fixture
def spark():
    return ColumnSparkline(HEADERS, ROWS)


@pytest.fixture
def renderer(spark):
    return SparklineRenderer(spark, col_width=10, spark_width=5)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers"):
        ColumnSparkline([], ROWS)


def test_headers_property(spark):
    assert spark.headers == HEADERS


def test_headers_returns_copy(spark):
    h = spark.headers
    h.append("extra")
    assert spark.headers == HEADERS


def test_to_buckets_empty():
    assert _to_buckets([], 4) == [0, 0, 0, 0]


def test_to_buckets_uniform():
    counts = _to_buckets([1.0, 1.0, 1.0], 3)
    assert sum(counts) == 3


def test_render_numeric_column_length(spark):
    result = spark.render("age", width=8)
    assert len(result) == 8


def test_render_non_numeric_column_returns_dashes(spark):
    result = spark.render("name", width=6)
    assert result == "------"


def test_render_unknown_column_raises(spark):
    with pytest.raises(KeyError):
        spark.render("unknown")


def test_render_width_less_than_one_raises(spark):
    with pytest.raises(ValueError, match="width"):
        spark.render("age", width=0)


def test_render_labeled_format(spark):
    result = spark.render_labeled("score", width=5)
    assert result.startswith("score: ")
    assert len(result) == len("score: ") + 5


def test_renderer_invalid_col_width_raises(spark):
    with pytest.raises(ValueError, match="col_width"):
        SparklineRenderer(spark, col_width=2)


def test_renderer_invalid_spark_width_raises(spark):
    with pytest.raises(ValueError, match="spark_width"):
        SparklineRenderer(spark, spark_width=0)


def test_renderer_col_width_property(renderer):
    assert renderer.col_width == 10


def test_renderer_spark_width_property(renderer):
    assert renderer.spark_width == 5


def test_renderer_render_returns_string(renderer):
    result = renderer.render()
    assert isinstance(result, str)
    assert len(result) > 0


def test_renderer_render_contains_all_headers(renderer):
    result = renderer.render()
    for col in HEADERS:
        assert col in result


def test_renderer_render_subset(renderer):
    result = renderer.render(columns=["age"])
    assert "age" in result
    assert "score" not in result
