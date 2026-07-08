from textual.widgets import Static


class StatusBar(Static):
    _buffer_count: int = 0

    def render(self) -> str:
        hints = "  ↑↓←→ navigate  / filter  s sort  h shuffle  space add  b buffer  p new playlist  q quit"
        buf = f"  [{self._buffer_count} in buffer]" if self._buffer_count else ""
        return f"{buf}{hints}"

    def update_buffer(self, count: int) -> None:
        self._buffer_count = count
        self.refresh()
