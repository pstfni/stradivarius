from textual.binding import Binding
from textual.message import Message
from textual.widgets import Input


class FilterBar(Input):
    """Single-line regex filter for the focused column. Hidden until activated with `/`."""

    BINDINGS = [Binding("escape", "cancel", "Cancel", show=False)]

    class Cancelled(Message):
        """Posted when the user dismisses the filter bar without keeping the filter."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.column: str | None = None

    def activate(self, column: str, current: str = "") -> None:
        self.column = column
        self.placeholder = f"filter {column.replace('_', ' ')} (regex)…"
        self.value = current
        self.add_class("visible")
        self.focus()

    def deactivate(self) -> None:
        self.remove_class("visible")

    def action_cancel(self) -> None:
        self.post_message(self.Cancelled())
