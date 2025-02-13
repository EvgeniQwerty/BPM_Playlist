# Spotify BPM Playlist Creator (Not Working)

**IMPORTANT:** This script no longer functions as intended because Spotify has restricted access to certain API endpoints. Read more about the changes here: [Spotify API Restrictions](https://developer.spotify.com/community/news/2024/02/spotify-api-changes/).

## Overview
This Python script allows users to create a Spotify playlist based on a specified BPM (beats per minute) range. It gathers tracks from the user's liked songs, saved playlists, and liked albums, filters them by BPM, and compiles them into a new playlist.

## Features
- Authenticate with Spotify API
- Fetch songs from liked tracks, saved playlists, and albums
- Filter songs based on BPM, energy, and danceability
- Create a new Spotify playlist with the selected tracks

## Requirements
- Python 3.7+
- A Spotify Developer account with API credentials
- Spotipy library
- dotenv library

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/EvgeniQwerty/BPM_Playlist.git
   cd BPM_Playlist
   ```
2. Install dependencies:
   ```sh
   pip install spotipy dotenv
   ```
3. Create a `.env` file in the project directory and add your Spotify credentials:
   ```sh
   SP_CLIENT_ID=your_client_id
   SP_CLIENT_SECRET=your_client_secret
   SP_REDIRECT_URI=https://open.spotify.com/
   SP_USERNAME=your_spotify_username
   ```

## Usage
Run the script and follow the prompts:
```sh
python main.py
```
You can also specify arguments:
```sh
python generate_playlist.py --bpm 120
python generate_playlist.py --bpm-range 100 130 --use-albums --use-playlists --use-liked
```

## Known Issues
- Due to recent Spotify API changes, access to certain user data is now restricted, leading to authentication and track-fetching failures.
