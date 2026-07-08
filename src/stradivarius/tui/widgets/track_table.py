import polars as pl
from rich.text import Text
from textual.widgets import DataTable

from stradivarius.data.schema import TrackRow

COLUMNS = ["playlist_name", "track_name", "artist", "album", "release_year", "added_at"]

# Catppuccin green: text colour for rows already added to the buffer.
BUFFERED_STYLE = "#a6e3a1"

# Max display width per column; longer cell values are trimmed with an ellipsis.
COLUMN_WIDTHS = {
    "playlist_name": 20,
    "track_name": 30,
    "artist": 20,
    "album": 25,
    "release_year": 6,
    "added_at": 10,
}


def _trim(value: str, width: int) -> str:
    return value if len(value) <= width else value[: width - 1] + "…"


class TrackTable(DataTable):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._df: pl.DataFrame = pl.DataFrame()
        self._filtered_df: pl.DataFrame = pl.DataFrame()
        self._sort_col: str | None = None
        self._sort_asc: bool = True
        self._active_filters: dict[str, str] = {}
        self._buffered_uris: set[str] = set()

    def load(self, df: pl.DataFrame) -> None:
        self._df = df
        self._active_filters.clear()
        self._sort_col = None
        self._refresh()

    # --- view rebuild ---

    def _refresh(self) -> None:
        """Recompute the visible frame from filters + sort, then redraw."""
        df = self._df
        for col, pattern in self._active_filters.items():
            if col in df.columns and pattern:
                try:
                    df = df.filter(pl.col(col).cast(pl.Utf8).str.contains(f"(?i){pattern}"))
                except Exception:
                    # partial / invalid regex while typing: skip this filter
                    pass
        if self._sort_col and self._sort_col in df.columns:
            df = df.sort(self._sort_col, descending=not self._sort_asc)
        self._filtered_df = df
        self._rebuild()

    def _rebuild(self) -> None:
        self.clear(columns=True)
        columns = [c for c in COLUMNS if c in self._filtered_df.columns]
        for col in columns:
            self.add_column(col.replace("_", " ").title(), key=col, width=COLUMN_WIDTHS[col])

        has_uri = "track_uri" in self._filtered_df.columns
        uris = self._filtered_df["track_uri"].to_list() if has_uri else [None] * self._filtered_df.height
        for row, uri in zip(self._filtered_df[columns].iter_rows(), uris):
            buffered = uri in self._buffered_uris
            cells = []
            for col, v in zip(columns, row):
                text = _trim(str(v) if v is not None else "", COLUMN_WIDTHS[col])
                cells.append(Text(text, style=BUFFERED_STYLE) if buffered else text)
            self.add_row(*cells)

    def set_buffered(self, uris: set[str]) -> None:
        self._buffered_uris = set(uris)
        coordinate = self.cursor_coordinate
        self._rebuild()
        self.move_cursor(row=coordinate.row, column=coordinate.column)

    # --- sorting / shuffling ---

    def shuffle(self) -> None:
        self._filtered_df = self._filtered_df.sample(fraction=1.0, shuffle=True)
        self._rebuild()

    def toggle_sort(self) -> None:
        col = self.current_column()
        if col is None:
            return
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True
        self._refresh()        

    # --- filtering ---

    def apply_filter(self, col: str, pattern: str) -> None:
        if pattern:
            self._active_filters[col] = pattern
        else:
            self._active_filters.pop(col, None)
        self._refresh()

    def clear_column_filter(self, col: str) -> None:
        if self._active_filters.pop(col, None) is not None:
            self._refresh()

    def clear_filters(self) -> None:
        if self._active_filters:
            self._active_filters.clear()
            self._refresh()

    def filter_value(self, col: str) -> str:
        return self._active_filters.get(col, "")

    # --- cursor helpers ---

    def current_column(self) -> str | None:
        columns = [c for c in COLUMNS if c in self._filtered_df.columns]
        if 0 <= self.cursor_column < len(columns):
            return columns[self.cursor_column]
        return None

    def focused_track(self) -> TrackRow | None:
        if self._filtered_df.is_empty() or not (0 <= self.cursor_row < self._filtered_df.height):
            return None
        row = self._filtered_df[COLUMNS].row(self.cursor_row)
        return TrackRow(
            playlist_name=row[0] or "",
            track_name=row[1] or "",
            artist=row[2] or "",
            album=row[3] or "",
            release_year=int(row[4]) if row[4] else None,
            added_at=row[5],
            track_uri=self._filtered_df["track_uri"][self.cursor_row],
        )
