from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from stradivarius.data.schema import TrackRow


class ComposeScreen(ModalScreen):
    def __init__(self, buffer: list[TrackRow]) -> None:
        super().__init__()
        self._buffer = buffer

    def compose(self) -> ComposeResult:
        yield Label("New playlist")
        yield Input(placeholder="Name", id="playlist-name")
        yield Input(placeholder="Description", id="playlist-description")
        yield Button("Create", id="create", variant="primary")
        yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
            return
        name = self.query_one("#playlist-name", Input).value.strip()
        description = self.query_one("#playlist-description", Input).value.strip()
        if not name:
            return
        self._create_playlist(name, description)
        self.dismiss()

    def _create_playlist(self, name: str, description: str) -> None:
        from chopin.managers.playlist import create_playlist, fill

        playlist = create_playlist(name, description)
        tracks = [t for t in self._buffer]  # TrackRow has .track_uri
        # chopin's fill expects TrackData; here we pass URIs directly via the client
        from chopin.client.endpoints import add_tracks_to_playlist

        add_tracks_to_playlist(playlist.id, [t.track_uri for t in tracks])
        self.app.notify(f"Created '{name}' with {len(tracks)} tracks.")
