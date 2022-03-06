# -*- coding: utf-8 -*-
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

def readParams():   
    file = open('settings.ini', 'r')
    lines = file.readlines()
    
    params = {
    'username':'',
    'danceability_min':40,
    'energy_min':15,
    'running_needed_bpm_low':160,
    'running_needed_bpm_high':180,
    'walking_needed_bpm_low':115,
    'walking_needed_bpm_high':120
    }
    
    for param in lines:
        if 'username' in param:
            params['username'] = param.split('=')[1].replace('\n', '')
        elif 'danceability_min' in param:
            params['danceability_min'] = int(param.split('=')[1].replace('\n', ''))    
        elif 'energy_min' in param:
            params['energy_min'] = int(param.split('=')[1].replace('\n', ''))
        elif 'running_needed_bpm_low' in param:
            params['running_needed_bpm_low'] = int(param.split('=')[1].replace('\n', ''))
        elif 'running_needed_bpm_high' in param:
            params['running_needed_bpm_high'] = int(param.split('=')[1].replace('\n', ''))
        elif 'walking_needed_bpm_low' in param:
            params['walking_needed_bpm_low'] = int(param.split('=')[1].replace('\n', ''))
        elif 'walking_needed_bpm_high' in param:
            params['walking_needed_bpm_high'] = int(param.split('=')[1].replace('\n', ''))
            
    return params            
    

def spotifyAuth(username):
    SPOTIPY_CLIENT_ID='YOUR CLIENT ID' #id from developer.spotify.com
    SPOTIPY_CLIENT_SECRET='YOUR SECRET' #secret from developer.spotify.com
    SPOTIPY_REDIRECT_URI = 'https://open.spotify.com/' #uri from developer.spotify.com
    scope = 'user-library-read playlist-modify-public playlist-read-private'

    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    token = util.prompt_for_user_token(username, scope, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)

    if token:
        sp = spotipy.Spotify(auth=token)
        return sp
    else:
        print("Can't get token for", username)
        return None

def chooseMode(params):      
    mode = None
    print('''
      Modes:
          1. Walking bpm
          2. Running bpm
          3. Your bpm
      ''')    
    while mode == None:
        mode = int(input('Choose mode: '))
    
    needed_bpm_low = None
    needed_bpm_high = None
    needed_bpm = None
    name_of_playlist = None
    
    #choosing bpm
    if mode == 3:
        while needed_bpm == None:
            needed_bpm = int(input('Write down needed bpm: '))
        needed_bpm_low = needed_bpm
        needed_bpm_high = needed_bpm
        name_of_playlist = '{} bmp'.format(needed_bpm)    
    elif mode == 2:
        needed_bpm_low = params['running_needed_bpm_low']
        needed_bpm_high = params['running_needed_bpm_high']
        needed_bpm = needed_bpm_high
        name_of_playlist = 'Running playlist ({}-{} bpm)'.format(needed_bpm_low, needed_bpm_high)
    else:
        needed_bpm_low = params['walking_needed_bpm_low']
        needed_bpm_high = params['walking_needed_bpm_high']
        needed_bpm = needed_bpm_high
        name_of_playlist = 'Walking playlist ({}-{} bpm)'.format(needed_bpm_low, needed_bpm_high)        

    print('\n')
    print('Tracks will be imported from playlists (personal and liked)')
    using_albums = None
    while using_albums != 'n' and using_albums != 'y': 
        using_albums = input('Using liked albums as well [y/n]: ')

    if using_albums == 'n':
        using_albums = False
    else:
        using_albums = True  
        
    return needed_bpm_low, needed_bpm_high, name_of_playlist, using_albums     

def createPlaylist(sp, needed_bpm_low, needed_bpm_high, name_of_playlist, using_albums, params):
    print('\n')    
    #create playlist
    bpm_playlist = sp.user_playlist_create(params['username'], name_of_playlist, True, False, 'playlist with certain bpm')
    print('Empty playlist created')

    playlists = sp.current_user_playlists()
    tracks = []
    uri_list = []
    number_of_tracks = 0

    for playlist in playlists['items']:
        playlist_id = playlist['id']
        tracks_in_playlist = sp.playlist_tracks(playlist_id)
        tracks.append(tracks_in_playlist)
        number_of_tracks += len(tracks_in_playlist['items'])
    
    print('Number of of tracks in user\'s playlists = {}'.format(number_of_tracks))
    ten_percent = int(number_of_tracks / 10)
    total_progress = 0    
    counter = 0
    print('Total progress (playlists) - {}%'.format(total_progress))

    for playlist in tracks:
        for track_data in playlist['items']:
            counter += 1
            if counter % ten_percent == 0:
                total_progress += 10
                print('Total progress (playlists) - {}%'.format(total_progress))     
        
            track_id = track_data['track']['id']
            if track_id != None:
                try:
                    features = sp.audio_features(track_id)
                    bpm = round(features[0]['tempo'])
                    danceability = features[0]['danceability'] * 100
                    energy = features[0]['energy'] * 100
                
                    if (bpm >= needed_bpm_low) and (bpm <= needed_bpm_high) and (danceability >= params['danceability_min']) and (energy >= params['energy_min']):
                        track_uri = track_data['track']['uri']
                        uri_list.append(track_uri)
                except:
                    pass                    
                    
    if total_progress < 100:
        total_progress += 10
        print('Total progress (playlists) - {}%'.format(total_progress))

    if using_albums:
        number_of_tracks = 0
        albums = sp.current_user_saved_albums()
    
        for album in albums['items']:
            number_of_tracks += len(album['album']['tracks']['items'])    
    
        print('\nNumber of tracks in albums = {}'.format(number_of_tracks))
        ten_percent = int(number_of_tracks / 10)
        total_progress = 0    
        counter = 0
    
        #print(albums['items'][0]['album']['tracks']['items'][0]['id'])
        for album in albums['items']:
            for track in album['album']['tracks']['items']:
                counter += 1
                if counter % ten_percent == 0:
                    total_progress += 10
                    print('Total progress (albums) - {}%'.format(total_progress))
                track_id = track['id']
                if track_id != None:
                    try:
                        features = sp.audio_features(track_id)
                        bpm = round(features[0]['tempo'])
                        danceability = round(features[0]['danceability'])
                        energy = round(features[0]['energy'])
                        if (bpm >= needed_bpm_low) and (bpm <= needed_bpm_high):
                            track_uri = track['uri']
                            uri_list.append(track_uri)
                    except:
                        pass                        

    if total_progress < 100:
        total_progress += 10
        print('Total progress (albums) - {}%'.format(total_progress))    

    print('\nDeleting duplicates...')
    print('Tracks before deleting duplicates - {}'.format(len(uri_list)))
    uri_list = list(set(uri_list))  
    print('Tracks after deleting duplicates - {}'.format(len(uri_list))) 
 
    print('\nAdding tracks to the playlist (may took a lot of time)') 
    for uri in uri_list: 
        uri_in_list = []
        uri_in_list.append(uri)              
        sp.user_playlist_add_tracks(params['username'], bpm_playlist['id'], uri_in_list)  
             
    print('Playlist {} bpm was created'.format(needed_bpm_low))      


if __name__ == '__main__':
    print('''
      -------------------------
      BPM Playlist Creator v0.3
      -------------------------  
      ''')
    params = readParams()  
    sp = spotifyAuth(params['username']) #log in
    if sp != None:
        needed_bpm_low, needed_bpm_high, name_of_playlist, using_albums = chooseMode(params)
        createPlaylist(sp, needed_bpm_low, needed_bpm_high, name_of_playlist, using_albums, params)              
