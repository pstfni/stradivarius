"""Schemas, dataclasses for stradivarius objects."""
from dataclasses import dataclass


@dataclass
class TrackRow:
    """Representation of a row in the library. It is a track with some metadata"""
    playlist_name: str
    track_name: str
    artist: str
    album: str
    release_year: int | None
    added_at: str | None
    track_uri: str
