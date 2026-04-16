import pytest
from csvlens.column_rename_engine import ColumnRenameEngine


@pytest.fixture
def engine():
    return ColumnRenameEngine(["id", "name", "age"])


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnRenameEngine([])


def test_headers_property(engine):
    assert engine.headers == ["id", "name", "age"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_initial_no_renames(engine):
    assert engine.renames == {}


def test_display_headers_no_renames(engine):
    assert engine.display_headers() == ["id", "name", "age"]


def test_set_rename(engine):
    engine.set_rename("name", "Full Name")
    assert engine.renames["name"] == "Full Name"


def test_display_headers_after_rename(engine):
    engine.set_rename("age", "Age (yrs)")
    disp = engine.display_headers()
    assert disp[2] == "Age (yrs)"
    assert disp[0] == "id"


def test_set_rename_invalid_column_raises(engine):
    with pytest.raises(KeyError):
        engine.set_rename("missing", "X")


def test_set_rename_blank_name_raises(engine):
    with pytest.raises(ValueError):
        engine.set_rename("id", "   ")


def test_clear_rename(engine):
    engine.set_rename("id", "ID")
    engine.clear_rename("id")
    assert "id" not in engine.renames


def test_clear_rename_nonexistent_is_noop(engine):
    engine.clear_rename("ghost")  # should not raise


def test_clear_all(engine):
    engine.set_rename("id", "ID")
    engine.set_rename("name", "Name")
    engine.clear_all()
    assert engine.renames == {}


def test_original_for_renamed(engine):
    engine.set_rename("name", "Full Name")
    assert engine.original_for("Full Name") == "name"


def test_original_for_unrenamed(engine):
    assert engine.original_for("id") == "id"


def test_original_for_unknown(engine):
    assert engine.original_for("ghost") is None
