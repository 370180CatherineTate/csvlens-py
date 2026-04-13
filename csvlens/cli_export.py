"""CLI helper for triggering exports from the interactive viewer."""

import sys
from pathlib import Path
from typing import List, Dict, Optional

from csvlens.export_engine import ExportEngine


def resolve_output_path(path_str: str) -> Path:
    """Validate and resolve the output file path."""
    path = Path(path_str).expanduser().resolve()
    if path.is_dir():
        raise IsADirectoryError(f"Output path is a directory: {path}")
    return path


def infer_format(path: Path, fmt: Optional[str]) -> str:
    """Infer export format from file extension if not explicitly provided."""
    if fmt:
        return fmt.lower()
    suffix = path.suffix.lstrip(".").lower()
    if suffix in ExportEngine.SUPPORTED_FORMATS:
        return suffix
    return "csv"


def run_export(
    headers: List[str],
    rows: List[Dict[str, str]],
    output_path: str,
    fmt: Optional[str] = None,
    visible_columns: Optional[List[str]] = None,
    silent: bool = False,
) -> int:
    """
    Export rows to a file. Returns 0 on success, 1 on failure.

    Parameters
    ----------
    headers:         Full list of CSV headers.
    rows:            Filtered/sorted rows to export.
    output_path:     Destination file path string.
    fmt:             Force format ('csv' or 'json'); inferred from extension if None.
    visible_columns: Restrict exported columns; all columns used if None.
    silent:          Suppress stdout messages when True.
    """
    try:
        path = resolve_output_path(output_path)
        format_ = infer_format(path, fmt)
        engine = ExportEngine(headers)
        content = engine.export(rows, format_, visible_columns)
        path.write_text(content, encoding="utf-8")
        if not silent:
            print(f"Exported {len(rows)} row(s) to {path} [{format_}]", file=sys.stdout)
        return 0
    except (ValueError, IsADirectoryError, OSError) as exc:
        print(f"Export failed: {exc}", file=sys.stderr)
        return 1
