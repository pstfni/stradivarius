from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Label

from stradivarius.data.schema import TrackRow


class BufferScreen(ModalScreen):
    """Read-only popup listing the tracks currently in the buffer."""

    BINDINGS = [
        ("escape", "close", "Close"),
        ("b", "close", "Close"),
        ("q", "close", "Close"),
    ]

    def __init__(self, buffer: list[TrackRow]) -> None:
        super().__init__()
        self._buffer = buffer

    def compose(self) -> ComposeResult:
        with Vertical(id="buffer-dialog"):
            yield Label(f"Buffer — {len(self._buffer)} track(s)", id="buffer-title")
            yield DataTable(id="buffer-table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#buffer-table", DataTable)
        table.add_columns("Track", "Artist", "Album")
        for track in self._buffer:
            table.add_row(track.track_name, track.artist, track.album)
        if not self._buffer:
            self.query_one("#buffer-title", Label).update("Buffer is empty")

    def action_close(self) -> None:
        self.dismiss()
