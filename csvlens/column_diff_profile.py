"""Track and compare column value snapshots for change detection."""
from __future__ import annotations
from typing import Dict, List, Optional


class ColumnDiffProfile:
    """Stores named snapshots of column values and compares them."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._snapshots: Dict[str, Dict[str, List[str]]] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def snapshot_names(self) -> List[str]:
        return list(self._snapshots.keys())

    def save_snapshot(self, name: str, rows: List[Dict[str, str]]) -> None:
        if not name or not name.strip():
            raise ValueError("snapshot name must not be blank")
        snapshot: Dict[str, List[str]] = {h: [] for h in self._headers}
        for row in rows:
            for h in self._headers:
                snapshot[h].append(row.get(h, ""))
        self._snapshots[name] = snapshot

    def delete_snapshot(self, name: str) -> None:
        self._snapshots.pop(name, None)

    def compare(self, name_a: str, name_b: str) -> Dict[str, List[int]]:
        """Return indices where values differ per column."""
        if name_a not in self._snapshots:
            raise KeyError(f"snapshot '{name_a}' not found")
        if name_b not in self._snapshots:
            raise KeyError(f"snapshot '{name_b}' not found")
        snap_a = self._snapshots[name_a]
        snap_b = self._snapshots[name_b]
        result: Dict[str, List[int]] = {}
        for h in self._headers:
            vals_a = snap_a.get(h, [])
            vals_b = snap_b.get(h, [])
            length = min(len(vals_a), len(vals_b))
            diffs = [i for i in range(length) if vals_a[i] != vals_b[i]]
            result[h] = diffs
        return result

    def diff_summary(self, name_a: str, name_b: str) -> Dict[str, int]:
        """Return count of differing rows per column."""
        return {col: len(idxs) for col, idxs in self.compare(name_a, name_b).items()}
