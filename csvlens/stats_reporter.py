"""Generates column statistics reports from a CSVLoader instance."""

from csvlens.column_stats import ColumnStats
from csvlens.csv_loader import CSVLoader


class StatsReporter:
    """Builds ColumnStats for each column in a loaded CSV file."""

    def __init__(self, loader: CSVLoader) -> None:
        self._loader = loader
        self._stats: dict[str, ColumnStats] | None = None

    def _build(self) -> None:
        columns: dict[str, list[str]] = {h: [] for h in self._loader.headers}
        for row in self._loader.iter_rows():
            for header, value in zip(self._loader.headers, row):
                columns[header].append(value)
        self._stats = {
            header: ColumnStats(header, values)
            for header, values in columns.items()
        }

    @property
    def stats(self) -> dict[str, ColumnStats]:
        if self._stats is None:
            self._build()
        return self._stats

    def get(self, column: str) -> ColumnStats | None:
        return self.stats.get(column)

    def print_summary(self, column: str | None = None) -> None:
        targets = (
            [self.stats[column]] if column and column in self.stats
            else list(self.stats.values())
        )
        for stat in targets:
            summary = stat.summary()
            print(f"\n--- {summary['name']} ---")
            print(f"  Total rows : {summary['total']}")
            print(f"  Nulls      : {summary['nulls']}")
            print(f"  Unique     : {summary['unique']}")
            print(f"  Numeric    : {summary['is_numeric']}")
            if summary["is_numeric"]:
                print(f"  Min        : {summary['min']}")
                print(f"  Max        : {summary['max']}")
                print(f"  Mean       : {summary.get('mean')}")
            top = summary["top_values"]
            if top:
                print("  Top values :")
                for val, cnt in top:
                    print(f"    {val!r:20s} x{cnt}")
