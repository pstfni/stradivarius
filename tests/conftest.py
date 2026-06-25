import json
from pathlib import Path
from unittest.mock import patch

import pytest
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData

from stradivarius.data.fetch import fetch_library

FIXTURES_DIR = Path(__file__).parent / "fixtures"
PLAYLIST_NAME = "dummy_playlist"


@pytest.fixture
def playlist():
    return PlaylistData(name=PLAYLIST_NAME, id="playlist_id", uri="spotify:playlist:playlist_id")


@pytest.fixture
def tracks():
    data = json.loads((FIXTURES_DIR / "playlist.json").read_text())
    return [TrackData.model_validate(t) for t in data]


@pytest.fixture
def library_df(playlist, tracks, tmp_path):
    with (
        patch("stradivarius.data.fetch.get_user_playlists", return_value=[playlist]),
        patch("stradivarius.data.fetch.get_playlist_tracks", return_value=tracks),
    ):
        return fetch_library(tmp_path / "library.parquet")


@pytest.fixture
def mock_library(library_df):
    with patch("stradivarius.tui.screens.library.load_library", return_value=library_df):
        yield library_df
