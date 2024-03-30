
from flask import Flask, flash, jsonify, render_template, session, redirect, url_for, request,Response
import requests
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from sklearn.metrics.pairwise import cosine_similarity
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import StringField, PasswordField, IntegerField, SubmitField,BooleanField, SubmitField,validators
from wtforms.validators import InputRequired, Length, EqualTo,NumberRange, DataRequired,Email
from flask_login import LoginManager, UserMixin
from flask_wtf import FlaskForm
from camera import *
import youtube_dlc as youtube_dl
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm,LoginForm

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/HP/OneDrive/Desktop/python/haar1/favdbn.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/HP/OneDrive/Desktop/python/SPOTIFY44/favdbn.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = "your_secret_key"  # Change this to a secret key for sessions

migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(100), unique=True)
    Password = db.Column(db.String(100))
    ConfirmPassword = db.Column(db.String(100))
  
class RegisterForm(FlaskForm):
   UserName = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
   Password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=80)])
   ConfirmPassword = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('Password')])
   Age = IntegerField('Age', validators=[InputRequired(), NumberRange(min=18, max=30, message='Age must be between 18 and 30')])  # Age between 18 and 30
   PhoneNumber = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=10)])
   Submit = SubmitField('Registerr')

class LoginForm(FlaskForm):
    UserName = StringField('Username', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    Submit = SubmitField('mlogin')

class ResetPasswordForm(FlaskForm):
    UserName = StringField('Username', validators=[validators.DataRequired()])
    Password = PasswordField('New Password', validators=[
        validators.DataRequired(),
        validators.Length(min=6, message="Password must be at least 6 characters")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('Password', message='Passwords do not match')
    ])



class FavTrackN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(255), nullable=False)
    artist_name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    preview_url = db.Column(db.String(255), nullable=True)


class FavTrackH(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(255), nullable=False)
    artist_name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    preview_url = db.Column(db.String(255), nullable=True)


class FavTrackSD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(255), nullable=False)
    artist_name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    preview_url = db.Column(db.String(255), nullable=True)


class FavTrackS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(255), nullable=False)
    artist_name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    preview_url = db.Column(db.String(255), nullable=True)

class FavTrackA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(255), nullable=False)
    artist_name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    preview_url = db.Column(db.String(255), nullable=True)

# Replace 'your_client_id' and 'your_client_secret' with your actual Spotify API credentials

CLIENT_ID = '2f4be40379e541d4a2f371bb791d907f'
CLIENT_SECRET = '216e0081a0b44963a0da4d0b01c481f8'
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
#---------------------------------------------------#

headings = ("Mood")
df1 = music_rec()
df1 = df1.head()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return "Hello, this is a Flask app!"

@app.route('/camm')
def mindex():
    
    df1 = music_rec()
    return render_template('index2.html', headings=headings, data=df1)


def gen(camera):
    while True:
        global df1
        frame, df1 = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/c')
def c():
    return render_template('cd.html')

@app.route('/t')
def gen_table():
    return df1.to_json(orient='records')

@app.route('/seeusers')
def view_users():
    users = User.query.all()  # Fetch all records from the User table
    return render_template('seeusers.html', users=users)

@app.route('/mlogin', methods=['GET', 'POST'])
def mlogin():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.UserName.data
        password = form.Password.data

        user = User.query.filter_by(UserName=username).first()
        if user and check_password_hash(user.Password, password):
            # Store the user's ID in the session
            #login_user(user, remember=form.remember.data)
            return redirect(url_for('c'))  # Redirect to the 'home' endpoint
        
        return '<h1>Invalid username or password</h1>'
    
    print("Form validation failed.")
    return render_template('login.html', form=form)

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        UserName  = request.form['username']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        user = User.query.filter_by(Username=UserName).first()

        if user:
            if new_password == confirm_password:
                user.password = generate_password_hash(new_password)
                db.session.commit()
                flash('Password updated successfully!', 'success')
                return redirect(url_for('see_users'))
            else:
                flash('Passwords do not match.', 'error')
        else:
            flash('User not found.', 'error')

    return render_template('forgot.html')
    


@app.route('/registerr', methods=['GET', 'POST'])
def registerr():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.UserName.data
        password = form.Password.data
        confirm_password = form.ConfirmPassword.data
        age = form.Age.data
        phone_number = form.PhoneNumber.data

        existing_user = User.query.filter_by(UserName=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('registerr'))

        if not (6 <= len(password) <= 20):
            flash('Password length should be between 6 and 20 characters.', 'error')
            return redirect(url_for('registerr'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('registerr'))

        if not (18 <= age <= 30):
            flash('Age must be between 18 and 30.', 'error')
            return redirect(url_for('registerr'))

        if len(phone_number) != 10 or not phone_number.isdigit():
            flash('Phone number should be 10 digits.', 'error')
            return redirect(url_for('registerr'))

        hashed_password = generate_password_hash(password)
        new_user = User(UserName=username, Password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('c'))

    return render_template('register.html', form=form)
        

       

@login_manager.user_loader

@app.route('/dashboard', methods=['GET', 'POST'])
def dashb():
    return render_template('dashboard.html')

#---------------------youtube------------------------------# 

@app.route('/emo')
def emo():
    return render_template('emoji.html')

@app.route('/submit_mood', methods=['POST'])
def submit_mood():
    selected_mood = request.form['selected_mood']

    if selected_mood == '😠':  # Check if the selected mood is '😠' (angry)
        return redirect(url_for('angry'))  # Redirect to the '/happy' route
    if selected_mood == '😢':  # Check if the selected mood is '😢' (sad)
        return redirect(url_for('sad'))  # Redirect to the '/happy' route
    if selected_mood == '😐':  
        return redirect(url_for('neutral'))  
    if selected_mood == '😊':  
        return redirect(url_for('happy'))  
    if selected_mood == '😲':  
        return redirect(url_for('sytr')) 

    # For other moods, redirect to 'play_page' as before
    return redirect(url_for('play_page', mood=selected_mood))


@app.route('/play/<mood>')
def play_page(mood):
    return f'Selected Mood: {mood} <br><a href="/emo">Back to Mood Slider</a>'


def get_entries(playlist_url, start, end):
    ydl_opts = {
        'format': 'best',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    if end > 10:
        ydl_opts['playliststart'] = start
        ydl_opts['playlistend'] = end
    else:
        ydl_opts['playliststart'] = start
        ydl_opts['playlistend'] = 10

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
        return result.get('entries') if result else None
@app.route('/happy')
def happy():
    # Replace this with your actual playlist retrieval logic
    playlist_url = 'https://www.youtube.com/playlist?list=PLmQj3u8DC8VuRskKePgLLijK0i78OGeMb'
    start_index = int(request.args.get('start', 1))
    end_index = start_index + 1 if start_index < 10 else start_index + 5

    # Replace this with your actual function to get playlist entries
    videos = get_entries(playlist_url, start_index, end_index)

    # Save song history for authenticated users
    
            # Create and add song history to the database
    

    # Render the template with the playlist videos
    return render_template('happy.html', videos=videos, start=start_index, end=end_index)


@app.route('/sytr')
def sytr():
    playlist_url = 'https://www.youtube.com/playlist?list=PLmQj3u8DC8VuC0GYJ9JewXGOq7ZmrA6mO'
    start_index = int(request.args.get('start', 1))
    end_index = start_index + 1 if start_index < 10 else start_index + 5  # Example: Change end range after 10 songs

    videos = get_entries(playlist_url, start_index, end_index)
    return render_template('surprised.html', videos=videos, start=start_index, end=end_index)
@app.route('/neutral')
def neutral():
    playlist_url = 'https://www.youtube.com/playlist?list=PLmQj3u8DC8VsNllU_DnAPw985MpLoM7i2'
    start_index = int(request.args.get('start', 1))  # Get the start index from the URL query parameter
    end_index = start_index + 1 if start_index < 10 else start_index + 5 
    videos = get_entries(playlist_url, start_index, end_index)
    return render_template('neutral.html', videos=videos, start=start_index, end=end_index )

@app.route('/sad')
def sad():
    playlist_url = 'https://www.youtube.com/playlist?list=PLgvCwzTvwOFg6aFPzBrtxXnbLkXiC7fki'
    start_index = int(request.args.get('start', 1))
    end_index = start_index + 1 if start_index < 10 else start_index + 5  # Example: Change end range after 10 songs

    videos = get_entries(playlist_url, start_index, end_index)
    return render_template('sad.html',videos=videos, start=start_index, end=end_index )

    
@app.route('/angry')
def angry():
     playlist_url = 'https://www.youtube.com/playlist?list=PLgvCwzTvwOFg6aFPzBrtxXnbLkXiC7fki'
     start_index = int(request.args.get('start', 1))
     end_index = start_index + 1 if start_index < 10 else start_index + 5  # Example: Change end range after 10 songs
     videos = get_entries(playlist_url, start_index, end_index)

     return render_template('angry.html', videos=videos, start=start_index, end=end_index)




 #------------------------spotify---------------------------# 
 

@app.route("/login")
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

        # Determine the mood based on the stored user_mood in the session
        mood = session.get('user_mood', 'unknown')

        # Redirect based on mood
        if mood == 'happy':
            return redirect(url_for('Hplaylist'))
        elif mood == 'neutral':
            return redirect(url_for('Nplaylist'))
        elif mood == 'sad':
            return redirect(url_for('SDplaylist'))
        elif mood == 'surprised':
            return redirect(url_for('Splaylist'))
        elif mood == 'angry':
            return redirect(url_for('Aplaylist'))
        else:
            flash('Invalid mood detected.')
            return redirect(url_for('index'))  # Redirect to a default route if mood is not recognized
    else:
        flash('Failed to authenticate.')

    return redirect(url_for('index'))

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
@app.route("/Nplaylist")
def Nplaylist():
    if "token" not in session:
        return redirect(url_for("Nplaylist"))

    # Get user profile information
    user_info = sp.current_user()
    user_display_name = user_info.get('display_name', 'User')

    # Check if images list is not empty before accessing its elements
    images = user_info.get('images', [])
    user_profile_picture = images[0]['url'] if images else None

    # Get playlist and track information
    headers = {"Authorization": f"Bearer {session['token']}"}
    recently_played_tracks = requests.get(API_BASE_URL + "/me/player/recently-played", headers=headers)

    if recently_played_tracks.status_code != 200:
        flash('Failed to fetch playlist. Please try again.')
        return redirect(url_for("login"))

    recently_played_tracks = recently_played_tracks.json()

    user_listening_history = [track['track']['id'] for track in recently_played_tracks['items']]

    playlist_id = "6Q7jbBUuyx5vDlZfDDpMF3"
    playlist_url = f"{API_BASE_URL}/playlists/{playlist_id}/tracks"
    response = requests.get(playlist_url, headers=headers)

    if response.status_code != 200:
        flash('Failed to fetch playlist tracks. Please try again.')
        return redirect(url_for("login"))

    data_1 = response.json()
    tracks_1 = []
    interaction_statuses_1 = []

    for item in data_1.get("items", []):
        track_name = item["track"]["name"]
        artist_name = item["track"]["artists"][0]["name"]

        # Get audio features for each track
        track_id = item["track"]["id"]

        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
        else:
            audio_features_data = {}  # Handle the case where audio features are not available

        # Append track information along with audio features to the list
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "audio_features": audio_features_data
        }
        tracks_1.append(track_info)

        # Check if the user has interacted with the track based on listening history
        user_interacted = 1 if track_id in user_listening_history else 0
        interaction_statuses_1.append(user_interacted)

    playlist_id_2 = "0V6MCQsj143PD8s9X2rwqj"
    playlist_url_2 = f"{API_BASE_URL}/playlists/{playlist_id_2}/tracks"
    response_2 = requests.get(playlist_url_2, headers=headers)

    if response_2.status_code != 200:
        flash('Failed to fetch playlist tracks. Please try again.')
        return redirect(url_for("login"))

    data_2 = response_2.json()
    tracks_2 = []
    interaction_statuses_2 = []
    audio_features_matrix_2 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    for item in data_2.get("items", []):
        track_id = item["track"]["id"]
        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
            if audio_features_data:
                # Append audio features to the matrix
                audio_features_matrix_2 = pd.concat([audio_features_matrix_2, pd.DataFrame(audio_features_data, index=[0])], ignore_index=True)
            else:
                # Handle the case where audio features are not available
                print(f"Audio features not available for track {track_id}")
        else:
            # Handle the case where audio features API request fails
            print(f"Failed to fetch audio features for track {track_id}")
            # Append track information along with audio features to the list
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "audio_features": audio_features_data
        }
        tracks_2.append(track_info)

        # Check if the user has interacted with the track based on listening history
        user_interacted = 1 if track_id in user_listening_history else 0
        interaction_statuses_2.append(user_interacted)

    # Add a new column for interaction status in the final DataFrames
    interaction_column_1 = pd.Series(interaction_statuses_1, name='interaction')
    audio_features_matrix_1 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    audio_features_matrix_1['interaction'] = interaction_column_1

    interaction_column_2 = pd.Series(interaction_statuses_2, name='interaction')
    #audio_features_matrix_2 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    audio_features_matrix_2['interaction'] = interaction_column_2

    user_profile = {}
    for track_id in user_listening_history:
        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
            for feature, value in audio_features_data.items():
                # Check if the value can be converted to a float
                try:
                    float_value = float(value)
                except ValueError:
                    continue  # Skip if not convertible

                # Convert the value to float before adding to the user profile
                user_profile[feature] = user_profile.get(feature, 0.0) + float_value

    num_tracks = len(user_listening_history)
    for feature, value in user_profile.items():
        user_profile[feature] = value / num_tracks

    session['user_profile'] = user_profile

    user_profile_vector = pd.DataFrame(session.get('user_profile', {}), index=[0])
    audio_features_matrix_2 = audio_features_matrix_2[user_profile_vector.columns]
    
    cosine_similarities = cosine_similarity(user_profile_vector, audio_features_matrix_2)
    similarity_scores = cosine_similarities[0]

    track_info_list = []
    for idx, score in enumerate(similarity_scores):
        track_name = data_2["items"][idx]["track"]["name"]
        artist_name = data_2["items"][idx]["track"]["artists"][0]["name"]

        # Fetch additional details (image URL and preview URL) from the Spotify API
        track_id = data_2["items"][idx]["track"]["id"]
        track_details_url = f"{API_BASE_URL}/tracks/{track_id}"
        track_details_response = requests.get(track_details_url, headers=headers)

        if track_details_response.status_code == 200:
            track_details = track_details_response.json()
            image_url = track_details.get("album", {}).get("images", [{}])[0].get("url")
            preview_url = track_details.get("preview_url")
        else:
            image_url = None
            preview_url = None

        # Build the track_info dictionary with additional details
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "similarity": score,
            "image_url": image_url,
            "preview_url": preview_url
        }
        track_info_list.append(track_info)

    # Sort the track_info_list based on similarity scores and take the top 20
    track_info_list = sorted(track_info_list, key=lambda x: x["similarity"], reverse=True)[:20]

        
    return render_template("Nplaylist.html", tracks=tracks_1 + tracks_2, user_display_name=user_display_name, user_profile_picture=user_profile_picture, user_profile=session.get('user_profile', {}), track_info_list=track_info_list)

@app.route("/Nfav_tracks")
def Nfav_tracks():
    # Query the database to get the favorite tracks
    fav_tracks = FavTrackN.query.all()

    # Render the template with the favorite tracks
    return render_template("fav2.html", fav_tracks=fav_tracks)

@app.route("/Hplaylist")
def Hplaylist():
    if "token" not in session:
        return redirect(url_for("Hplaylist"))

    # Get user profile information
    user_info = sp.current_user()
    user_display_name = user_info.get('display_name', 'User')

    # Check if images list is not empty before accessing its elements
    images = user_info.get('images', [])
    user_profile_picture = images[0]['url'] if images else None

    # Get playlist and track information
    headers = {"Authorization": f"Bearer {session['token']}"}
    recently_played_tracks = requests.get(API_BASE_URL + "/me/player/recently-played", headers=headers)

    if recently_played_tracks.status_code != 200:
        flash('Failed to fetch playlist. Please try again.')
        return redirect(url_for("login"))

    recently_played_tracks = recently_played_tracks.json()

    user_listening_history = [track['track']['id'] for track in recently_played_tracks['items']]

    playlist_id = "6Q7jbBUuyx5vDlZfDDpMF3"
    playlist_url = f"{API_BASE_URL}/playlists/{playlist_id}/tracks"
    response = requests.get(playlist_url, headers=headers)

    if response.status_code != 200:
        flash('Failed to fetch playlist tracks. Please try again.')
        return redirect(url_for("login"))

    data_1 = response.json()
    tracks_1 = []
    interaction_statuses_1 = []

    for item in data_1.get("items", []):
        track_name = item["track"]["name"]
        artist_name = item["track"]["artists"][0]["name"]

        # Get audio features for each track
        track_id = item["track"]["id"]

        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
        else:
            audio_features_data = {}  # Handle the case where audio features are not available

        # Append track information along with audio features to the list
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "audio_features": audio_features_data
        }
        tracks_1.append(track_info)

        # Check if the user has interacted with the track based on listening history
        user_interacted = 1 if track_id in user_listening_history else 0
        interaction_statuses_1.append(user_interacted)

    playlist_id_2 = "0Kjw1ITpNXtrh3Xn5JV1oU"
    playlist_url_2 = f"{API_BASE_URL}/playlists/{playlist_id_2}/tracks"
    response_2 = requests.get(playlist_url_2, headers=headers)

    if response_2.status_code != 200:
        flash('Failed to fetch playlist tracks. Please try again.')
        return redirect(url_for("login"))

    data_2 = response_2.json()
    tracks_2 = []
    interaction_statuses_2 = []
    audio_features_matrix_2 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    for item in data_2.get("items", []):
        track_id = item["track"]["id"]
        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
            if audio_features_data:
                # Append audio features to the matrix
                audio_features_matrix_2 = pd.concat([audio_features_matrix_2, pd.DataFrame(audio_features_data, index=[0])], ignore_index=True)
            else:
                # Handle the case where audio features are not available
                print(f"Audio features not available for track {track_id}")
        else:
            # Handle the case where audio features API request fails
            print(f"Failed to fetch audio features for track {track_id}")
            # Append track information along with audio features to the list
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "audio_features": audio_features_data
        }
        tracks_2.append(track_info)

        # Check if the user has interacted with the track based on listening history
        user_interacted = 1 if track_id in user_listening_history else 0
        interaction_statuses_2.append(user_interacted)

    # Add a new column for interaction status in the final DataFrames
    interaction_column_1 = pd.Series(interaction_statuses_1, name='interaction')
    audio_features_matrix_1 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    audio_features_matrix_1['interaction'] = interaction_column_1

    interaction_column_2 = pd.Series(interaction_statuses_2, name='interaction')
    #audio_features_matrix_2 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    audio_features_matrix_2['interaction'] = interaction_column_2

    user_profile = {}
    for track_id in user_listening_history:
        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
            for feature, value in audio_features_data.items():
                # Check if the value can be converted to a float
                try:
                    float_value = float(value)
                except ValueError:
                    continue  # Skip if not convertible

                # Convert the value to float before adding to the user profile
                user_profile[feature] = user_profile.get(feature, 0.0) + float_value

    num_tracks = len(user_listening_history)
    for feature, value in user_profile.items():
        user_profile[feature] = value / num_tracks

    session['user_profile'] = user_profile

    user_profile_vector = pd.DataFrame(session.get('user_profile', {}), index=[0])
    audio_features_matrix_2 = audio_features_matrix_2[user_profile_vector.columns]
    cosine_similarities = cosine_similarity(user_profile_vector, audio_features_matrix_2)
    similarity_scores = cosine_similarities[0]

    track_info_list = []
    for idx, score in enumerate(similarity_scores):
        track_name = data_2["items"][idx]["track"]["name"]
        artist_name = data_2["items"][idx]["track"]["artists"][0]["name"]

        # Fetch additional details (image URL and preview URL) from the Spotify API
        track_id = data_2["items"][idx]["track"]["id"]
        track_details_url = f"{API_BASE_URL}/tracks/{track_id}"
        track_details_response = requests.get(track_details_url, headers=headers)

        if track_details_response.status_code == 200:
            track_details = track_details_response.json()
            image_url = track_details.get("album", {}).get("images", [{}])[0].get("url")
            preview_url = track_details.get("preview_url")
        else:
            image_url = None
            preview_url = None

        # Build the track_info dictionary with additional details
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "similarity": score,
            "image_url": image_url,
            "preview_url": preview_url
        }
        track_info_list.append(track_info)

    # Sort the track_info_list based on similarity scores and take the top 20
    track_info_list = sorted(track_info_list, key=lambda x: x["similarity"], reverse=True)[:20]

        
    return render_template("Hplaylist.html", tracks=tracks_1 + tracks_2, user_display_name=user_display_name, user_profile_picture=user_profile_picture, user_profile=session.get('user_profile', {}), track_info_list=track_info_list)

@app.route("/Hfav_tracks")
def Hfav_tracks():
    # Query the database to get the favorite tracks
    fav_tracks = FavTrackH.query.all()

    # Render the template with the favorite tracks
    return render_template("fav2.html", fav_tracks=fav_tracks)


@app.route("/SDplaylist")
def SDplaylist():
    if "token" not in session:
        return redirect(url_for("SDplaylist"))

    # Get user profile information
    user_info = sp.current_user()
    user_display_name = user_info.get('display_name', 'User')

    # Check if images list is not empty before accessing its elements
    images = user_info.get('images', [])
    user_profile_picture = images[0]['url'] if images else None

    # Get playlist and track information
    headers = {"Authorization": f"Bearer {session['token']}"}
    recently_played_tracks = requests.get(API_BASE_URL + "/me/player/recently-played", headers=headers)

    if recently_played_tracks.status_code != 200:
        flash('Failed to fetch playlist. Please try again.')
        return redirect(url_for("login"))

    recently_played_tracks = recently_played_tracks.json()

    user_listening_history = [track['track']['id'] for track in recently_played_tracks['items']]

    playlist_id = "6Q7jbBUuyx5vDlZfDDpMF3"
    playlist_url = f"{API_BASE_URL}/playlists/{playlist_id}/tracks"
    response = requests.get(playlist_url, headers=headers)

    if response.status_code != 200:
        flash('Failed to fetch playlist tracks. Please try again.')
        return redirect(url_for("login"))

    data_1 = response.json()
    tracks_1 = []
    interaction_statuses_1 = []

    for item in data_1.get("items", []):
        track_name = item["track"]["name"]
        artist_name = item["track"]["artists"][0]["name"]

        # Get audio features for each track
        track_id = item["track"]["id"]

        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
        else:
            audio_features_data = {}  # Handle the case where audio features are not available

        # Append track information along with audio features to the list
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "audio_features": audio_features_data
        }
        tracks_1.append(track_info)

        # Check if the user has interacted with the track based on listening history
        user_interacted = 1 if track_id in user_listening_history else 0
        interaction_statuses_1.append(user_interacted)

    playlist_id_2 = "781EJqdEVft7bDm4XpKMpG"
    playlist_url_2 = f"{API_BASE_URL}/playlists/{playlist_id_2}/tracks"
    response_2 = requests.get(playlist_url_2, headers=headers)

    if response_2.status_code != 200:
        flash('Failed to fetch playlist tracks. Please try again.')
        return redirect(url_for("login"))

    data_2 = response_2.json()
    tracks_2 = []
    interaction_statuses_2 = []
    audio_features_matrix_2 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    for item in data_2.get("items", []):
        track_id = item["track"]["id"]
        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
            if audio_features_data:
                # Append audio features to the matrix
                audio_features_matrix_2 = pd.concat([audio_features_matrix_2, pd.DataFrame(audio_features_data, index=[0])], ignore_index=True)
            else:
                # Handle the case where audio features are not available
                print(f"Audio features not available for track {track_id}")
        else:
            # Handle the case where audio features API request fails
            print(f"Failed to fetch audio features for track {track_id}")
            # Append track information along with audio features to the list
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "audio_features": audio_features_data
        }
        tracks_2.append(track_info)

        # Check if the user has interacted with the track based on listening history
        user_interacted = 1 if track_id in user_listening_history else 0
        interaction_statuses_2.append(user_interacted)

    # Add a new column for interaction status in the final DataFrames
    interaction_column_1 = pd.Series(interaction_statuses_1, name='interaction')
    audio_features_matrix_1 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    audio_features_matrix_1['interaction'] = interaction_column_1

    interaction_column_2 = pd.Series(interaction_statuses_2, name='interaction')
    #audio_features_matrix_2 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    audio_features_matrix_2['interaction'] = interaction_column_2

    user_profile = {}
    for track_id in user_listening_history:
        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
            for feature, value in audio_features_data.items():
                # Check if the value can be converted to a float
                try:
                    float_value = float(value)
                except ValueError:
                    continue  # Skip if not convertible

                # Convert the value to float before adding to the user profile
                user_profile[feature] = user_profile.get(feature, 0.0) + float_value

    num_tracks = len(user_listening_history)
    for feature, value in user_profile.items():
        user_profile[feature] = value / num_tracks

    session['user_profile'] = user_profile

    user_profile_vector = pd.DataFrame(session.get('user_profile', {}), index=[0])
    audio_features_matrix_2 = audio_features_matrix_2[user_profile_vector.columns]
    cosine_similarities = cosine_similarity(user_profile_vector, audio_features_matrix_2)
    similarity_scores = cosine_similarities[0]

    track_info_list = []
    for idx, score in enumerate(similarity_scores):
        track_name = data_2["items"][idx]["track"]["name"]
        artist_name = data_2["items"][idx]["track"]["artists"][0]["name"]

        # Fetch additional details (image URL and preview URL) from the Spotify API
        track_id = data_2["items"][idx]["track"]["id"]
        track_details_url = f"{API_BASE_URL}/tracks/{track_id}"
        track_details_response = requests.get(track_details_url, headers=headers)

        if track_details_response.status_code == 200:
            track_details = track_details_response.json()
            image_url = track_details.get("album", {}).get("images", [{}])[0].get("url")
            preview_url = track_details.get("preview_url")
        else:
            image_url = None
            preview_url = None

        # Build the track_info dictionary with additional details
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "similarity": score,
            "image_url": image_url,
            "preview_url": preview_url
        }
        track_info_list.append(track_info)

    track_info_list = sorted(track_info_list, key=lambda x: x["similarity"], reverse=True)[:20]
    # Sort the track_info_list based on similarity scores in ascending order and take the first 20
        
    return render_template("SDplaylist.html", tracks=tracks_1 + tracks_2, user_display_name=user_display_name, user_profile_picture=user_profile_picture, user_profile=session.get('user_profile', {}), track_info_list=track_info_list)

@app.route("/SDfav_tracks")
def SDfav_tracks():
    # Query the database to get the favorite tracks
    fav_tracks = FavTrackSD.query.all()

    # Render the template with the favorite tracks
    return render_template("fav2.html", fav_tracks=fav_tracks)

@app.route("/Splaylist")
def Splaylist():
    if "token" not in session:
        return redirect(url_for("Splaylist"))

    # Get user profile information
    user_info = sp.current_user()
    user_display_name = user_info.get('display_name', 'User')

    # Check if images list is not empty before accessing its elements
    images = user_info.get('images', [])
    user_profile_picture = images[0]['url'] if images else None

    # Get playlist and track information
    headers = {"Authorization": f"Bearer {session['token']}"}
    recently_played_tracks = requests.get(API_BASE_URL + "/me/player/recently-played", headers=headers)

    if recently_played_tracks.status_code != 200:
        flash('Failed to fetch playlist. Please try again.')
        return redirect(url_for("login"))

    recently_played_tracks = recently_played_tracks.json()

    user_listening_history = [track['track']['id'] for track in recently_played_tracks['items']]

    playlist_id = "6Q7jbBUuyx5vDlZfDDpMF3"
    playlist_url = f"{API_BASE_URL}/playlists/{playlist_id}/tracks"
    response = requests.get(playlist_url, headers=headers)

    if response.status_code != 200:
        flash('Failed to fetch playlist tracks. Please try again.')
        return redirect(url_for("login"))

    data_1 = response.json()
    tracks_1 = []
    interaction_statuses_1 = []

    for item in data_1.get("items", []):
        track_name = item["track"]["name"]
        artist_name = item["track"]["artists"][0]["name"]

        # Get audio features for each track
        track_id = item["track"]["id"]

        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
        else:
            audio_features_data = {}  # Handle the case where audio features are not available

        # Append track information along with audio features to the list
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "audio_features": audio_features_data
        }
        tracks_1.append(track_info)

        # Check if the user has interacted with the track based on listening history
        user_interacted = 1 if track_id in user_listening_history else 0
        interaction_statuses_1.append(user_interacted)

    playlist_id_2 = "61f4ObFpy1wH01uJgsmpsi"
    playlist_url_2 = f"{API_BASE_URL}/playlists/{playlist_id_2}/tracks"
    response_2 = requests.get(playlist_url_2, headers=headers)

    if response_2.status_code != 200:
        flash('Failed to fetch playlist tracks. Please try again.')
        return redirect(url_for("login"))

    data_2 = response_2.json()
    tracks_2 = []
    interaction_statuses_2 = []
    audio_features_matrix_2 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    for item in data_2.get("items", []):
        track_id = item["track"]["id"]
        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
            if audio_features_data:
                # Append audio features to the matrix
                audio_features_matrix_2 = pd.concat([audio_features_matrix_2, pd.DataFrame(audio_features_data, index=[0])], ignore_index=True)
            else:
                # Handle the case where audio features are not available
                print(f"Audio features not available for track {track_id}")
        else:
            # Handle the case where audio features API request fails
            print(f"Failed to fetch audio features for track {track_id}")
            # Append track information along with audio features to the list
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "audio_features": audio_features_data
        }
        tracks_2.append(track_info)

        # Check if the user has interacted with the track based on listening history
        user_interacted = 1 if track_id in user_listening_history else 0
        interaction_statuses_2.append(user_interacted)

    # Add a new column for interaction status in the final DataFrames
    interaction_column_1 = pd.Series(interaction_statuses_1, name='interaction')
    audio_features_matrix_1 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    audio_features_matrix_1['interaction'] = interaction_column_1

    interaction_column_2 = pd.Series(interaction_statuses_2, name='interaction')
    #audio_features_matrix_2 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    audio_features_matrix_2['interaction'] = interaction_column_2

    user_profile = {}
    for track_id in user_listening_history:
        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
            for feature, value in audio_features_data.items():
                # Check if the value can be converted to a float
                try:
                    float_value = float(value)
                except ValueError:
                    continue  # Skip if not convertible

                # Convert the value to float before adding to the user profile
                user_profile[feature] = user_profile.get(feature, 0.0) + float_value

    num_tracks = len(user_listening_history)
    for feature, value in user_profile.items():
        user_profile[feature] = value / num_tracks

    session['user_profile'] = user_profile

    user_profile_vector = pd.DataFrame(session.get('user_profile', {}), index=[0])
    audio_features_matrix_2 = audio_features_matrix_2[user_profile_vector.columns]
    cosine_similarities = cosine_similarity(user_profile_vector, audio_features_matrix_2)
    similarity_scores = cosine_similarities[0]

    track_info_list = []
    for idx, score in enumerate(similarity_scores):
        track_name = data_2["items"][idx]["track"]["name"]
        artist_name = data_2["items"][idx]["track"]["artists"][0]["name"]

        # Fetch additional details (image URL and preview URL) from the Spotify API
        track_id = data_2["items"][idx]["track"]["id"]
        track_details_url = f"{API_BASE_URL}/tracks/{track_id}"
        track_details_response = requests.get(track_details_url, headers=headers)

        if track_details_response.status_code == 200:
            track_details = track_details_response.json()
            image_url = track_details.get("album", {}).get("images", [{}])[0].get("url")
            preview_url = track_details.get("preview_url")
        else:
            image_url = None
            preview_url = None

        # Build the track_info dictionary with additional details
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "similarity": score,
            "image_url": image_url,
            "preview_url": preview_url
        }
        track_info_list.append(track_info)

    # Sort the track_info_list based on similarity scores and take the top 20
    track_info_list = sorted(track_info_list, key=lambda x: x["similarity"], reverse=True)[:20]

        
    return render_template("Splaylist.html", tracks=tracks_1 + tracks_2, user_display_name=user_display_name, user_profile_picture=user_profile_picture, user_profile=session.get('user_profile', {}), track_info_list=track_info_list)

@app.route("/Sfav_tracks")
def Sfav_tracks():
    # Query the database to get the favorite tracks
    fav_tracks = FavTrackS.query.all()

    # Render the template with the favorite tracks
    return render_template("fav2.html", fav_tracks=fav_tracks)

@app.route("/Aplaylist")
def Aplaylist():
    if "token" not in session:
        return redirect(url_for("Aplaylist"))

    # Get user profile information
    user_info = sp.current_user()
    user_display_name = user_info.get('display_name', 'User')

    # Check if images list is not empty before accessing its elements
    images = user_info.get('images', [])
    user_profile_picture = images[0]['url'] if images else None

    # Get playlist and track information
    headers = {"Authorization": f"Bearer {session['token']}"}
    recently_played_tracks = requests.get(API_BASE_URL + "/me/player/recently-played", headers=headers)

    if recently_played_tracks.status_code != 200:
        flash('Failed to fetch playlist. Please try again.')
        return redirect(url_for("login"))

    recently_played_tracks = recently_played_tracks.json()

    user_listening_history = [track['track']['id'] for track in recently_played_tracks['items']]

    playlist_id = "6Q7jbBUuyx5vDlZfDDpMF3"
    playlist_url = f"{API_BASE_URL}/playlists/{playlist_id}/tracks"
    response = requests.get(playlist_url, headers=headers)

    if response.status_code != 200:
        flash('Failed to fetch playlist tracks. Please try again.')
        return redirect(url_for("login"))

    data_1 = response.json()
    tracks_1 = []
    interaction_statuses_1 = []

    for item in data_1.get("items", []):
        track_name = item["track"]["name"]
        artist_name = item["track"]["artists"][0]["name"]

        # Get audio features for each track
        track_id = item["track"]["id"]

        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
        else:
            audio_features_data = {}  # Handle the case where audio features are not available

        # Append track information along with audio features to the list
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "audio_features": audio_features_data
        }
        tracks_1.append(track_info)

        # Check if the user has interacted with the track based on listening history
        user_interacted = 1 if track_id in user_listening_history else 0
        interaction_statuses_1.append(user_interacted)

    playlist_id_2 = "1AjA0UkKScDkgiQfnmErEG"
    playlist_url_2 = f"{API_BASE_URL}/playlists/{playlist_id_2}/tracks"
    response_2 = requests.get(playlist_url_2, headers=headers)

    if response_2.status_code != 200:
        flash('Failed to fetch playlist tracks. Please try again.')
        return redirect(url_for("login"))

    data_2 = response_2.json()
    tracks_2 = []
    interaction_statuses_2 = []
    audio_features_matrix_2 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    for item in data_2.get("items", []):
        track_id = item["track"]["id"]
        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
            if audio_features_data:
                # Append audio features to the matrix
                audio_features_matrix_2 = pd.concat([audio_features_matrix_2, pd.DataFrame(audio_features_data, index=[0])], ignore_index=True)
            else:
                # Handle the case where audio features are not available
                print(f"Audio features not available for track {track_id}")
        else:
            # Handle the case where audio features API request fails
            print(f"Failed to fetch audio features for track {track_id}")
            # Append track information along with audio features to the list
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "audio_features": audio_features_data
        }
        tracks_2.append(track_info)

        # Check if the user has interacted with the track based on listening history
        user_interacted = 1 if track_id in user_listening_history else 0
        interaction_statuses_2.append(user_interacted)

    # Add a new column for interaction status in the final DataFrames
    interaction_column_1 = pd.Series(interaction_statuses_1, name='interaction')
    audio_features_matrix_1 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    audio_features_matrix_1['interaction'] = interaction_column_1

    interaction_column_2 = pd.Series(interaction_statuses_2, name='interaction')
    #audio_features_matrix_2 = pd.DataFrame(columns=['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'])
    audio_features_matrix_2['interaction'] = interaction_column_2

    user_profile = {}
    for track_id in user_listening_history:
        audio_features_url = f"{API_BASE_URL}/audio-features/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)

        if audio_features_response.status_code == 200:
            audio_features_data = audio_features_response.json()
            for feature, value in audio_features_data.items():
                # Check if the value can be converted to a float
                try:
                    float_value = float(value)
                except ValueError:
                    continue  # Skip if not convertible

                # Convert the value to float before adding to the user profile
                user_profile[feature] = user_profile.get(feature, 0.0) + float_value

    num_tracks = len(user_listening_history)
    for feature, value in user_profile.items():
        user_profile[feature] = value / num_tracks

    session['user_profile'] = user_profile

    user_profile_vector = pd.DataFrame(session.get('user_profile', {}), index=[0])
    audio_features_matrix_2 = audio_features_matrix_2[user_profile_vector.columns]
    
    cosine_similarities = cosine_similarity(user_profile_vector, audio_features_matrix_2)
    similarity_scores = cosine_similarities[0]

    track_info_list = []
    for idx, score in enumerate(similarity_scores):
        track_name = data_2["items"][idx]["track"]["name"]
        artist_name = data_2["items"][idx]["track"]["artists"][0]["name"]

        # Fetch additional details (image URL and preview URL) from the Spotify API
        track_id = data_2["items"][idx]["track"]["id"]
        track_details_url = f"{API_BASE_URL}/tracks/{track_id}"
        track_details_response = requests.get(track_details_url, headers=headers)

        if track_details_response.status_code == 200:
            track_details = track_details_response.json()
            image_url = track_details.get("album", {}).get("images", [{}])[0].get("url")
            preview_url = track_details.get("preview_url")
        else:
            image_url = None
            preview_url = None

        # Build the track_info dictionary with additional details
        track_info = {
            "name": track_name,
            "artist": artist_name,
            "similarity": score,
            "image_url": image_url,
            "preview_url": preview_url
        }
        track_info_list.append(track_info)

    # Sort the track_info_list based on similarity scores and take the top 20
    track_info_list = sorted(track_info_list, key=lambda x: x["similarity"], reverse=True)[:20]

        
    return render_template("Aplaylist.html", tracks=tracks_1 + tracks_2, user_display_name=user_display_name, user_profile_picture=user_profile_picture, user_profile=session.get('user_profile', {}), track_info_list=track_info_list)

@app.route("/Afav_tracks")
def Afav_tracks():
    # Query the database to get the favorite tracks
    fav_tracks = FavTrackA.query.all()

    # Render the template with the favorite tracks
    return render_template("fav2.html", fav_tracks=fav_tracks)

# Update the add_to_favorites route
@app.route('/Nadd_to_favorites', methods=['POST'])
def add_to_favorites():
    data = request.json

    # Ensure the keys match the ones sent from the client
    new_fav_track = FavTrackN(
        track_name=data['track_name'],
        artist_name=data['artist_name'],
        image_url=data['image_url'],
        preview_url=data['preview_url']
    )

    try:
        db.session.add(new_fav_track)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/Hadd_to_favorites', methods=['POST'])
def Hadd_to_favorites():
    data = request.json

    # Ensure the keys match the ones sent from the client
    new_fav_track = FavTrackH(
        track_name=data['track_name'],
        artist_name=data['artist_name'],
        image_url=data['image_url'],
        preview_url=data['preview_url']
    )

    try:
        db.session.add(new_fav_track)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/Sadd_to_favorites', methods=['POST'])
def Sadd_to_favorites():
    data = request.json

    # Ensure the keys match the ones sent from the client
    new_fav_track = FavTrackS(
        track_name=data['track_name'],
        artist_name=data['artist_name'],
        image_url=data['image_url'],
        preview_url=data['preview_url']
    )

    try:
        db.session.add(new_fav_track)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/SDadd_to_favorites', methods=['POST'])
def SDadd_to_favorites():
    data = request.json

    # Ensure the keys match the ones sent from the client
    new_fav_track = FavTrackSD(
        track_name=data['track_name'],
        artist_name=data['artist_name'],
        image_url=data['image_url'],
        preview_url=data['preview_url']
    )

    try:
        db.session.add(new_fav_track)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

    
@app.route('/Aadd_to_favorites', methods=['POST'])
def Aadd_to_favorites():
    data = request.json

    # Ensure the keys match the ones sent from the client
    new_fav_track = FavTrackA(
        track_name=data['track_name'],
        artist_name=data['artist_name'],
        image_url=data.get('image_url'),  # Use .get() to handle potential absence of 'image_url'
        preview_url=data['preview_url']
    )

    try:
        db.session.add(new_fav_track)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route("/search_and_listen", methods=["GET", "POST"])
def search_and_listen():
    if 'token' not in session:
        return redirect(url_for('search_and_listen'))

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
                    "sres.html",
                    track_name=track_name,
                    artist_name=artist_name,
                    track_image_url=track_image_url,
                    preview_url=preview_url,
                )
            else:
                return render_template(
                    "sres.html", error="No results found."
                )

    return render_template("snl.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


