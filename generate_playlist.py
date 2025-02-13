import argparse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import os
from dotenv import load_dotenv

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SP_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SP_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SP_REDIRECT_URI")
USERNAME = os.getenv("SP_USERNAME")

def spotify_auth(username):
    scope = 'user-library-read playlist-modify-public playlist-read-private'
    
    client_credentials_manager = SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, 
        client_secret=SPOTIPY_CLIENT_SECRET
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    token = util.prompt_for_user_token(
        username, scope, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
    )

    if token:
        sp = spotipy.Spotify(auth=token)
        
        try:
            user = sp.current_user()
            print(f"Authenticated as: {user['id']}")
        except spotipy.SpotifyException as e:
            print(f"Authentication error: {e}")
        
        return sp
    else:
        print("Can't get token for", USERNAME)
        return None

def parse_arguments():
    parser = argparse.ArgumentParser(description='Create a Spotify playlist based on BPM.')
    parser.add_argument('--bpm', type=int, help='Target BPM')
    parser.add_argument('--bpm-range', type=int, nargs=2, metavar=('LOW', 'HIGH'), help='BPM range')
    parser.add_argument('--use-albums', action='store_true', help='Include liked albums')
    parser.add_argument('--use-playlists', action='store_true', help='Include saved playlists')
    parser.add_argument('--use-liked', action='store_true', help='Include liked songs')
    return parser.parse_args()

def get_user_input():
    bpm_low, bpm_high, bpm = None, None, None
    print('''\nModes:\n    1. Specific BPM\n    2. BPM Range''')
    while bpm is None and bpm_low is None:
        mode = input('Choose mode (1 or 2): ').strip()
        if mode == '1':
            bpm = int(input('Enter desired BPM: ').strip())
        elif mode == '2':
            bpm_low = int(input('Enter BPM low: ').strip())
            bpm_high = int(input('Enter BPM high: ').strip())
    use_albums = input('Include liked albums? (y/n): ').strip().lower() == 'y'
    use_playlists = input('Include saved playlists? (y/n): ').strip().lower() == 'y'
    use_liked = input('Include liked songs? (y/n): ').strip().lower() != 'n'
    return bpm_low, bpm_high, bpm, use_albums, use_playlists, use_liked

def fetch_tracks_from_playlists(sp):
    tracks = []
    try:
        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            tracks.extend(sp.playlist_tracks(playlist['id'])['items'])
    except Exception as e:
        print(f"Error fetching playlist tracks: {e}")
    return tracks

def fetch_tracks_from_albums(sp):
    tracks = []
    try:
        albums = sp.current_user_saved_albums()
        for album in albums['items']:
            tracks.extend(album['album']['tracks']['items'])
    except Exception as e:
        print(f"Error fetching album tracks: {e}")
    return tracks

def fetch_tracks_from_liked(sp):
    tracks = []
    try:
        liked_tracks = sp.current_user_saved_tracks()
        for track in liked_tracks['items']:
            tracks.append(track['track'])
    except Exception as e:
        print(f"Error fetching liked tracks: {e}")
    return tracks

def filter_tracks(sp, tracks, bpm_low, bpm_high, bpm):
    bpm_low = bpm_low if bpm_low else bpm
    bpm_high = bpm_high if bpm_high else bpm
    valid_tracks = []
    for track in tracks:
        track_id = track.get('track', {}).get('id')
        if track_id:
            try:
                features = sp.audio_features([track_id])[0]
                if features and bpm_low <= round(features['tempo']) <= bpm_high \
                        and features['danceability'] * 100 >= 40 \
                        and features['energy'] * 100 >= 15:
                    valid_tracks.append(track['track']['uri'])
            except Exception:
                continue
    return list(set(valid_tracks))

def create_playlist(sp, username, bpm_low, bpm_high, bpm, use_albums, use_playlists, use_liked):
    bpm_label = f'{bpm} BPM Playlist' if bpm else f'{bpm_low}-{bpm_high} BPM Playlist'
    playlist = sp.user_playlist_create(username, bpm_label, public=True, description='Generated playlist')
    print(f'Playlist "{bpm_label}" created successfully.')
    tracks = []
    if use_playlists:
        tracks.extend(fetch_tracks_from_playlists(sp))
    if use_albums:
        tracks.extend(fetch_tracks_from_albums(sp))
    if use_liked:
        tracks.extend(fetch_tracks_from_liked(sp))
    filtered_tracks = filter_tracks(sp, tracks, bpm_low, bpm_high, bpm)
    for i in range(0, len(filtered_tracks), 100):
        sp.user_playlist_add_tracks(username, playlist['id'], filtered_tracks[i:i + 100])
    print(f'Added {len(filtered_tracks)} tracks to the playlist.')

if __name__ == '__main__':
    args = parse_arguments()
    
    bpm_low, bpm_high = args.bpm_range if args.bpm_range else (None, None)
    bpm = args.bpm
    use_albums = args.use_albums
    use_playlists = args.use_playlists
    use_liked = args.use_liked
    
    if not any([args.bpm, args.bpm_range]):
        bpm_low, bpm_high, bpm, use_albums, use_playlists, use_liked = get_user_input()
    sp = spotify_auth(USERNAME)
    if sp:
        create_playlist(sp, USERNAME, bpm_low, bpm_high, bpm, use_albums, use_playlists, use_liked)
