import polars as pl
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input

from stradivarius.data import TrackRow, load_library
from stradivarius.tui.widgets.filter_bar import FilterBar
from stradivarius.tui.widgets.status_bar import StatusBar
from stradivarius.tui.widgets.track_table import TrackTable


class LibraryScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "sort", "Sort"),
        ("h", "shuffle", "Shuffle"),
        ("space", "select_track", "Add to buffer"),
        ("b", "toggle_buffer", "Buffer"),
        ("p", "compose_playlist", "New playlist"),
        ("slash", "start_filter", "Filter"),
        ("escape", "clear_filters", "Clear filters"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._df: pl.DataFrame = pl.DataFrame()
        self._buffer: list[TrackRow] = []

    def compose(self) -> ComposeResult:
        yield TrackTable(id="track-table")
        yield FilterBar(id="filter-bar")
        yield StatusBar(id="status-bar")

    def on_mount(self) -> None:
        try:
            self._df = load_library()
            self.query_one(TrackTable).load(self._df)
        except FileNotFoundError:
            self.notify("No library found. Run with --sync to load your playlists.", severity="warning")

    # --- actions ---

    def action_sort(self) -> None:
        self.query_one(TrackTable).toggle_sort()

    def action_shuffle(self) -> None:
        self.query_one(TrackTable).shuffle()

    def action_select_track(self) -> None:
        table = self.query_one(TrackTable)
        row = table.focused_track()
        if row and row.track_uri not in {t.track_uri for t in self._buffer}:
            self._buffer.append(row)
            self.query_one(StatusBar).update_buffer(len(self._buffer))
            table.set_buffered({t.track_uri for t in self._buffer})

    def action_toggle_buffer(self) -> None:
        from stradivarius.tui.screens.buffer import BufferScreen

        self.app.push_screen(BufferScreen(self._buffer))

    def action_compose_playlist(self) -> None:
        if not self._buffer:
            return
        from stradivarius.tui.screens.compose import ComposeScreen

        self.app.push_screen(ComposeScreen(self._buffer))

    def action_start_filter(self) -> None:
        table = self.query_one(TrackTable)
        col = table.current_column()
        if col is None:
            return
        self.query_one(FilterBar).activate(col, table.filter_value(col))

    def action_clear_filters(self) -> None:
        self.query_one(TrackTable).clear_filters()

    def action_quit(self) -> None:
        self.app.exit()

    # --- filter bar wiring ---

    def on_input_changed(self, event: Input.Changed) -> None:
        bar = event.input
        if isinstance(bar, FilterBar) and bar.column:
            self.query_one(TrackTable).apply_filter(bar.column, event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if isinstance(event.input, FilterBar):
            self._close_filter()

    def on_filter_bar_cancelled(self, event: FilterBar.Cancelled) -> None:
        bar = self.query_one(FilterBar)
        if bar.column:
            self.query_one(TrackTable).clear_column_filter(bar.column)
        self._close_filter()

    def _close_filter(self) -> None:
        self.query_one(FilterBar).deactivate()
        self.query_one(TrackTable).focus()
