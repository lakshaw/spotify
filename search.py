
from flask import Flask, flash, jsonify, render_template, session, redirect, url_for, request
import requests
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secret key for sessions

# Replace 'your_client_id' and 'your_client_secret' with your actual Spotify API credentials
CLIENT_ID = 'd14690ae60e3456b94cf5abfe63f3113'
CLIENT_SECRET = '54db5a5264ff4e5ea4fc8bcd4d2b2727'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'

sp_oauth = SpotifyOAuth(
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    scope="user-read-recently-played user-library-read playlist-read-private",
)

sp = spotipy.Spotify(auth_manager=sp_oauth)
# Spotify API endpoints
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"


scope="user-read-recently-played user-library-read playlist-read-private"

@app.route("/")
def login():
    auth_query_parameters = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": scope,
        "client_id": CLIENT_ID,
    }

    auth_url = f"{AUTH_URL}?{requests.compat.urlencode(auth_query_parameters)}"
    return redirect(auth_url)

def get_user_listening_history(access_token):
    sp = spotipy.Spotify(auth=access_token)
    results = sp.current_user_recently_played()
    listening_history = []

    for item in results['items']:
        track_id = item['track']['id']
        listening_history.append(track_id)

    return listening_history

@app.route("/callback")
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    if 'access_token' in token_info:
        session['token'] = token_info['access_token']  # Update 'token_info' to 'token'
        # Get and store user listening history
        user_listening_history = get_user_listening_history(token_info['access_token'])
        session['user_listening_history'] = user_listening_history
    else:
        flash('Failed to authenticate.')

    return redirect(url_for('search_and_listen'))

def get_token(auth_code):
    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(TOKEN_URL, data=token_data)
    return response.json()

@app.route("/search_and_listen", methods=["GET", "POST"])
def search_and_listen():
    if 'token' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        query = request.form.get("query")

        if query:
            sp = spotipy.Spotify(auth=session['token'])
            results = sp.search(q=query, type="track", limit=1)

            if "tracks" in results and "items" in results["tracks"]:
                track_info = results["tracks"]["items"][0]
                track_name = track_info["name"]
                artist_name = track_info["artists"][0]["name"]
                track_id = track_info["id"]
                preview_url = track_info["preview_url"]

                # Use the image from the album field
                if "album" in track_info and "images" in track_info["album"]:
                    track_image_url = track_info["album"]["images"][0]["url"]
                else:
                    # Use a default image URL if no image is available
                    track_image_url = "https://placekitten.com/200/200"  # Replace with your default image URL

                return render_template(
                    "snl.html",
                    track_name=track_name,
                    artist_name=artist_name,
                    track_image_url=track_image_url,
                    preview_url=preview_url,
                )
            else:
                return render_template(
                    "snl.html", error="No results found."
                )

    return render_template("snl.html")


if __name__ == "__main__":
    app.run(debug=True)


