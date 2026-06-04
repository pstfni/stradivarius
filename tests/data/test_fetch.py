from datetime import date
from unittest.mock import patch

import pytest
from chopin.schemas.album import AlbumData
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData

from stradivarius.data.fetch import fetch_library, load_library
from stradivarius.data.schema import TrackRow


# --- fetch_library ---


@patch("stradivarius.data.fetch.get_playlist_tracks")
@patch("stradivarius.data.fetch.get_user_playlists")
def test_fetch_library(mock_playlists, mock_tracks, playlist, tracks, tmp_path):
    mock_playlists.return_value = [playlist]
    mock_tracks.return_value = tracks

    output_path = tmp_path / "library.parquet"
    df = fetch_library(output_path)

    assert output_path.exists()
    assert len(df) == 5
    assert set(df.columns) == set(TrackRow.__annotations__.keys())

    assert df["playlist_name"].unique()[0]== playlist.name

    first_song = df.filter(df["track_name"].str.contains("Hydrogen"))
    assert first_song["artist"][0] == "Boards of Canada"
    assert first_song["album"][0] == "Inferno"


@pytest.mark.parametrize("n_playlists", [1, 2, 3])
@patch("stradivarius.data.fetch.get_playlist_tracks")
@patch("stradivarius.data.fetch.get_user_playlists")
def test_fetch_library_multiple_playlists_combined(mock_playlists, mock_tracks, n_playlists, tracks, tmp_path):
    playlists = [
        PlaylistData(name=f"playlist_{i}", id=f"id_{i}", uri=f"spotify:playlist:id_{i}")
        for i in range(n_playlists)
    ]
    mock_playlists.return_value = playlists
    mock_tracks.return_value = tracks  # same 5 tracks per playlist

    df = fetch_library(tmp_path / "library.parquet")

    assert len(df) == 5 * n_playlists

@patch("stradivarius.data.fetch.get_user_playlists")
def test_fetch_library_no_playlists(mock_playlists, tmp_path):
    mock_playlists.return_value = []
    df = fetch_library(tmp_path / "library.parquet")

    assert df.is_empty()

# --- load_library ---


@patch("stradivarius.data.fetch.get_playlist_tracks")
@patch("stradivarius.data.fetch.get_user_playlists")
def test_load_library(mock_playlists, mock_tracks, playlist, tracks, tmp_path):
    mock_playlists.return_value = [playlist]
    mock_tracks.return_value = tracks
    output = tmp_path / "library.parquet"
    df = fetch_library(output)

    loaded_df = load_library(output)
    assert len(df) == 5
    assert loaded_df.columns == df.columns
    assert loaded_df.item(0,3) == df.item(0,3)


def test_load_library_missing_file(tmp_path):
    with pytest.raises(ValueError):
        load_library(tmp_path / "nonexistent.parquet")
