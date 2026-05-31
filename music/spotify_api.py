from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

client_id = "2f01a7760dcb4453937c52b8b6e5eaf9"
client_secret = "2f8a55e8cee24f88b254fbc84d61e7ee"

spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
)

def get_featured_songs():

    result = spotify.search(
        q="top hits",
        type="track",
        limit=20
    )

    songs = []

    for track in result["tracks"]["items"]:

        songs.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "image": track["album"]["images"][0]["url"],
            "spotify_url": track["external_urls"]["spotify"],
            "preview_url": track.get("preview_url")
        })

    return songs


def search_songs(query):

    result = spotify.search(
        q=query,
        type="track",
        limit=20
    )

    songs = []

    for track in result["tracks"]["items"]:

        songs.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "image": track["album"]["images"][0]["url"],
            "spotify_url": track["external_urls"]["spotify"],
            "preview_url": track["preview_url"]
        })

    return songs