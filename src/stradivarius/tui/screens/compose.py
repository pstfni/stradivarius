from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from stradivarius.data.schema import TrackRow


class ComposeScreen(ModalScreen):
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, buffer: list[TrackRow]) -> None:
        super().__init__()
        self._buffer = buffer

    def compose(self) -> ComposeResult:
        with Vertical(id="compose-dialog"):
            yield Label(f"New playlist — {len(self._buffer)} track(s)", id="compose-title")
            yield Input(placeholder="Name", id="playlist-name")
            yield Input(placeholder="Description", id="playlist-description")
            with Horizontal(id="compose-actions"):
                yield Button("Create", id="create", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#playlist-name", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
            return
        self._submit()

    def on_input_submitted(self) -> None:
        self._submit()

    def action_cancel(self) -> None:
        self.dismiss()

    def _submit(self) -> None:
        name = self.query_one("#playlist-name", Input).value.strip()
        if not name:
            self.query_one("#playlist-name", Input).focus()
            return
        description = self.query_one("#playlist-description", Input).value.strip()
        self._create_playlist(name, description)
        self.dismiss()

    def _create_playlist(self, name: str, description: str) -> None:
        from chopin.client.endpoints import add_tracks_to_playlist
        from chopin.managers.playlist import create_playlist

        playlist = create_playlist(name, description)
        add_tracks_to_playlist(playlist.id, [t.track_uri for t in self._buffer])
        self.app.notify(f"Created '{name}' with {len(self._buffer)} tracks.")
