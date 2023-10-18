import os
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
# Change with your username
SPOTIFY_USERNAME = 11167852623

year = input("What year you would like to travel to? (YYYY-MM-DD format): ")

URL = f"https://www.billboard.com/charts/hot-100/{year}/"
response = requests.get(URL)

soup = BeautifulSoup(response.text, "html.parser")
all_titles = soup.select("li ul li h3")
top_100 = [titles.getText().strip() for titles in all_titles]

# Get access to the spotify authentication with spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public",
                                               client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri="http://localhost/",
                                               show_dialog=True,
                                               username=SPOTIFY_USERNAME
                                               )
                     )
USERNAME = sp.current_user()["id"]

# Finds all the URIs of the songs and add them in a list
song_URI = []
for song_name in top_100:
    try:
        result = sp.search(q=song_name, type="track", limit=1)
    except IndexError:
        print(f"{song_name} doesn't exist in Spotify. Skipped.")
    else:
        song_URI.append(result["tracks"]["items"][0]["uri"])

# Returns all the playlists of the user
playlists = sp.current_user_playlists()

# Checks if the playlist is already created
found_playlist = False
for name in playlists["items"]:
    if f"{year} Billboard 100" in name["name"]:
        found_playlist = True
        break

#  Create the playlist if it doesn't exist
if found_playlist:
    print("The playlist already exists")
else:
    create_playlist = sp.user_playlist_create(USERNAME,
                                              f"{year} Billboard 100",
                                              public=True,
                                              description=f'Top 100 Songs of {year}'
                                              )
    # Get the id of the playlist
    playlist_ID = create_playlist["id"]
    print(f"Your link for the playlist is: {create_playlist['external_urls']['spotify']}")

    # Add all the songs into the playlist
    sp.playlist_add_items(playlist_ID, song_URI)

    playlist = sp.playlist(playlist_ID)
    print(f"Playlist ID: {playlist_ID}")
    print(f"Playlist Name: {playlist['name']}")
    print(f"Number of Tracks: {len(playlist['tracks']['items'])}")
