import click

from stradivarius.data import fetch_library
from stradivarius.tui.app import Stradivarius


@click.command()
@click.option("--sync", is_flag=True, default=False, help="Reload the user library from Spotify before launching.")
def app(sync: bool) -> None:
    """Launch the stradivarius TUI."""
    if sync:
        fetch_library()
    Stradivarius().run()
