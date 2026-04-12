"""Tests for csvlens.highlight utilities."""

import pytest
from csvlens.highlight import highlight_spans, highlight_cell, strip_ansi


def test_no_spans_returns_original():
    assert highlight_spans("hello", []) == "hello"


def test_single_span_wraps_correctly():
    result = highlight_spans("hello world", [(6, 11)])
    assert strip_ansi(result) == "hello world"
    assert "world" in result
    # ANSI codes present
    assert "\033[" in result


def test_multiple_spans():
    text = "abcabc"
    spans = [(0, 1), (3, 4)]
    result = highlight_spans(text, spans)
    plain = strip_ansi(result)
    assert plain == text


def test_highlight_cell_convenience():
    result = highlight_cell("foo bar", [(4, 7)])
    assert strip_ansi(result) == "foo bar"
    assert "\033[" in result


def test_strip_ansi_removes_codes():
    coloured = "\033[1;33mhello\033[0m world"
    assert strip_ansi(coloured) == "hello world"


def test_strip_ansi_no_codes():
    assert strip_ansi("plain text") == "plain text"


def test_full_string_span():
    text = "match"
    result = highlight_spans(text, [(0, len(text))])
    assert strip_ansi(result) == text
    assert "\033[" in result


def test_span_at_start():
    text = "hello world"
    result = highlight_spans(text, [(0, 5)])
    assert strip_ansi(result) == text


def test_span_at_end():
    text = "hello world"
    result = highlight_spans(text, [(6, 11)])
    assert strip_ansi(result) == text
