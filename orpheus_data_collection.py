'''
This is the data collection stage for the **Orpheus**.
By using the Spotify Web API for collecting albums and tracks
For a given Artist_name(Hilary Hahn in my example check out a brief overview from Spotify, link in the source)
Writing the audio features(acousticness,tempo...) for the songs into a csv file.

About H.Hahn(brief): Three-time Grammy Award-winning violinist Hilary Hahn is renowned for her virtuosity,
                          expansive interpretations, and creative programming.
             source: https://open.spotify.com/artist/5JdT0LYJdlPbTC58p60WTX/about
               wiki: https://en.wikipedia.org/wiki/Hilary_Hahn

Credits*:
This was adapted from a blog post in medium.com by the user@RareLoot on 28/02/2020
here: https://medium.com/@RareLoot/extracting-spotify-data-on-your-favourite-artist-via-python-d58bc92a4330
'''
import config
import webbrowser
import os
import time
import numpy as np
import pandas as pd
import spotipy
import download_csv as dc                                          # Basic function for yes_no
from spotipy.oauth2 import SpotifyClientCredentials                # To access Spotify credentials

client_id = config.client_id
client_secret = config.client_secret
sp = spotipy.Spotify(
    client_credentials_manager=config.client_credentials_manager)  # Spotify object to access API
name = "Hilary Hahn"                                               # Give the name artist
result = sp.search(name)                                           # Searching the artist
#test_ans = result['tracks']['items'][0]['artists']
artist_uri = result['tracks']['items'][0]['artists'][0]['uri']     # Store Artist's uri
sp_albums = sp.artist_albums(artist_uri, album_type='album')       # Collect all of the artist's albums

#Store artist's albums' names' and uris in separate lists
album_names = []
album_uris = []
for i in range(len(sp_albums['items'])):
    album_names.append(sp_albums['items'][i]['name'])
    album_uris.append(sp_albums['items'][i]['uri'])

# Extract key album track data from each album
def albumSongs(uri):
    album = uri
    spotify_albums[album] = {}                                     # Dictionary for that specific album uri(like a unique identifier)

    spotify_albums[album]['album'] = []
    spotify_albums[album]['track_number'] = []
    spotify_albums[album]['id'] = []
    spotify_albums[album]['name'] = []
    spotify_albums[album]['uri'] = []
    tracks = sp.album_tracks(album)

    for n in range(len(tracks['items'])):
        spotify_albums[album]['album'].append(album_names[album_count])
        spotify_albums[album]['track_number'].append(
                  tracks['items'][n]['track_number'])
        spotify_albums[album]['id'].append(tracks['items'][n]['id'])
        spotify_albums[album]['name'].append(tracks['items'][n]['name'])
        spotify_albums[album]['uri'].append(tracks['items'][n]['uri'])


# Pull the track data from each album URI and
# add to the new dictionary for album data
spotify_albums = {}
album_count = 0
for i in album_uris:                                                # For each album
    albumSongs(i)
    print("Album " + str(album_names[album_count]) \
        + " songs has been added to spotify_albums dictionary")
    album_count+=1                                                  # Updates album count once all tracks have been added

# Store key-values to store audio features
def audio_features(album):
    spotify_albums[album]['acousticness'] = []
    spotify_albums[album]['danceability'] = []
    spotify_albums[album]['energy'] = []
    spotify_albums[album]['instrumentalness'] = []
    spotify_albums[album]['liveness'] = []
    spotify_albums[album]['loudness'] = []
    spotify_albums[album]['speechiness'] = []
    spotify_albums[album]['tempo'] = []
    spotify_albums[album]['valence'] = []
    spotify_albums[album]['popularity'] = []

    track_count = 0
    for track in spotify_albums[album]['uri']:

        features = sp.audio_features(track)                           # Audio features for each track

        # Appending relevant key-value
        spotify_albums[album]['acousticness'].        \
            append(features[0]['acousticness'])

        spotify_albums[album]['danceability'].        \
            append(features[0]['danceability'])

        spotify_albums[album]['energy'].              \
            append(features[0]['energy'])

        spotify_albums[album]['instrumentalness'].    \
            append(features[0]['instrumentalness'])

        spotify_albums[album]['liveness'].append(features[0]['liveness'])
        spotify_albums[album]['loudness'].append(features[0]['loudness'])
        spotify_albums[album]['speechiness'].append(features[0]['speechiness'])
        spotify_albums[album]['tempo'].append(features[0]['tempo'])
        spotify_albums[album]['valence'].append(features[0]['valence'])

        #popularity is stored elsewhere
        popular = sp.track(track)
        spotify_albums[album]['popularity'].append(popular['popularity'])
        track_count+=1


# Random delay to avoid request avalanche for the Spotify's API
sleep_min = 2
sleep_max = 5
start_time = time.time()
request_count = 0
for i in spotify_albums:
    audio_features(i)
    request_count+=1
    if request_count % 5 == 0:
        print(str(request_count) + " albums processed")
        time.sleep(np.random.uniform(sleep_min, sleep_max))
        print(f'Loop #: {request_count}')
        print(f'Elapsed Time: {time.time() - start_time} seconds')

""" for ei in spotify_albums:
    print(ei) """
print(f'The artist:{name} has {len(spotify_albums)} albums')

# Organising data into a dictionary first.
# Then create dataframe using pandas.
dic_df = {}
dic_df['album'] = []
dic_df['track_number'] = []
dic_df['id'] = []
dic_df['name'] = []
dic_df['uri'] = []
dic_df['acousticness'] = []
dic_df['danceability'] = []
dic_df['energy'] = []
dic_df['instrumentalness'] = []
dic_df['liveness'] = []
dic_df['loudness'] = []
dic_df['speechiness'] = []
dic_df['tempo'] = []
dic_df['valence'] = []
dic_df['popularity'] = []
for album in spotify_albums:
    for feature in spotify_albums[album]:
        dic_df[feature].extend(spotify_albums[album][feature])
len(dic_df['album'])
df = pd.DataFrame.from_dict(dic_df)                                  # Exploiting Pandas' dataframe

# Dealing with duplications
print(f'Before removing any duplicate track(s) there are {len(df)} tracks')
final_df = df.sort_values('popularity',ascending=False).drop_duplicates('name').sort_index()
print(f'After removing duplicate track(s) considering few popular songs {len(final_df)}')
print('Writing to csv file........................')
final_df.to_csv("Hilary_Hahn.csv")
print('Completed writing the data to csv.')

if dc.yes_or_no():
    csv_path = 'file:///'+os.getcwd()+'/' + 'Hilary_Hahn.csv'
    webbrowser.open(csv_path)
    print("Download completed")
else:
    print('The question was just me being *formal*. You have your csv file already'
        + ' \n  (՞ ਊ՞)--☞  <<I GOTChA!!! \n  \n')



