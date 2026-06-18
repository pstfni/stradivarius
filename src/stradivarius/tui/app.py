from textual.app import App, ComposeResult

from stradivarius.tui.screens.library import LibraryScreen


class Stradivarius(App):
    CSS_PATH = "stradivarius.tcss"

    def on_mount(self) -> None:
        self.push_screen(LibraryScreen())
