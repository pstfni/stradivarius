import json
from pathlib import Path

import pytest
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def playlist():
    return PlaylistData(name="dummy_playlist", id="playlist_id", uri="spotify:playlist:playlist_id")


@pytest.fixture
def tracks():
    data = json.loads((FIXTURES_DIR / "playlist.json").read_text())
    return [TrackData.model_validate(t) for t in data]
