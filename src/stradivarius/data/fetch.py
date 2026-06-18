from pathlib import Path

import polars as pl
import logging

from stradivarius.constants import LIBRARY_PATH
from stradivarius.data.schema import TrackRow
from chopin.client.endpoints import get_playlist_tracks, get_user_playlists
from chopin.constants import constants

logger = logging.Logger(__name__)

def fetch_library(output_path: Path = LIBRARY_PATH) -> pl.DataFrame:
    """Use chopin to fetch the user _library_, all its playlists.
    
    See schema.py for details around the format chosen to store a playlist.

    Args:
        output_path: the path where the library should be saved. 
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[TrackRow] = []
    for playlist in get_user_playlists():
        if playlist.id not in constants.PROTECTED_PLAYLISTS_ID:
            continue
        logger.info(f"Parsing playlist {playlist.name}")
        for track in get_playlist_tracks(playlist.id):
            rows.append(
                TrackRow(
                    playlist_name=playlist.name,
                    track_name=track.name,
                    artist=track.artists[0].name if track.artists else "",
                    album=track.album.name if track.album else "",
                    release_year=_year(track.album.release_date) if track.album else None,
                    added_at=str(track.added_at) if track.added_at else None,
                    track_uri=track.uri,
                )
            )

    df = pl.DataFrame([r.__dict__ for r in rows])
    df.write_parquet(output_path)
    return df


def load_library(path: Path = LIBRARY_PATH) -> pl.DataFrame:
    """Load the library in path as a dataframe.

    Args: 
        path: path where the library is saved. A parquet file is expected.

    Returns:
        A dataframe with the user' library.
    """
    if not path.exists():
        raise ValueError(f"Library not found at {path}")
    return pl.read_parquet(path)


def _year(release_date) -> int | None:
    if release_date is None:
        return None
    try:
        return int(str(release_date)[:4])
    except (ValueError, TypeError):
        return None
