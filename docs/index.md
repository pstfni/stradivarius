# :violin: stradivarius

Stradivarius is a TUI app to view, filter, sort and select tracks of a Spotify user's playlists.

## Installation

### Clone the repo

```bash
git clone git@github.com:pstfni/stradivarius.git
cd stradivarius/
```

### Prerequisites

A spotify developer account is required, to interact with playlists and create the playlist from the selected tracks.

Create a [Spotify Developer](https://developer.spotify.com/dashboard/) account and an app. The dummy application
will let you use the service.
Here is an example of a configuration for your application:
```md 
Application Name: "app"
Website: _Not needed_
Redirect URIs: `http://127.0.0.1:8888/callback`
Bundle IDs: _Not needed_
Android Packages: _Not needed_
```

Once your application is setup in the Spotify Web interface, you can add your credentials in a `.env` file.

```
client_id=""
client_secret=""
scope="user-library-modify,playlist-modify-public,user-library-read"
```

More infos about the scopes and what they do is available on the [Spotify Developer documentation](https://developer.spotify.com/documentation/general/guides/authorization/scopes/)

### Dependencies

`stradivarius` use uv to run the app and install its dependencies.

To install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Running the app

Where you've cloned the repository, run :

```bash
uv run stradivarius
```

!!! note "First time running the app"
    If it is your first time running the app, you will need to populate the available playlists and their songs.
    You can do so by running:

    ```bash
    uv run stradivarius --sync
    ```

    This will fetch your user's playlist.

You should see the stradivarius TUI app:

![docs/img/app.png]

The app will let you add songs in a _buffer_. When you're done, you can create a playlist with said songs from the buffer. The newly created playlist will be added to your user's playlists.

### Commands

Commands are described in the footer bar:

- Navigate between rows and colums with keyboard arrows
- Add a track in the "buffer" with `space`.
- Sort the active column by pressing `s`. Press `s` again to cycle through the sort order.
- Filter on the existing column by pressing `\`. This will let you input a regex for filtering the column.
- You can combine filters between columns. Go back to the column of interest and press `\` again to view the existing filter and change it.
- At all time, you can remove all active filters with `esc`.

If you are happy with the selection:
- You can see it with `b`, which will display the current "buffer"
- Create your playlist by pressing `p`. Choose a name for the new playlist and confirm :sparkles:


## Developers

Put yourself in the stradivarius venv. In your stradivarius directory:

```bash
uv venv 
source .venv /bin/activate
```

Install the dependencies:

```bash
uv sync --extra dev
```

Run the tests:
```bash
pytest
```

## Disclaimer

`stradivarius` relies heavily on:
- [chopin](https://pstfni.github.io/chopin/) to retrieve, summarize and create playlists.
- [textual](https://textual.textualize.io/) for the TUI app.

The TUI app was built using Claude.