import random
import json
import requests
from .exceptions import ResponseException
from .secrets import spotify_user_id, spotify_token
from flask import Flask
app = Flask(__name__)


class CreatePlaylist:

    def __init__(self, weather_code, temp, location):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        if weather_code > 751 and weather_code < 804:
            self.weather = "sunny"
        elif weather_code < 621:
            self.weather = "rainy"
        else:
            self.weather = "cloudy"
        self.weather_corr = {"sunny": is_sunny, "rainy": is_rainy, "cloudy": is_cloudy}
        self.temp = temp
        self.location = location
        self.playlist_link = None

    # Create an empty playlist, include weather conditions in description
    def create_playlist(self):
        request_body = json.dumps({
            "name": "Your {} day playlist".format(self.weather),
            "description": "Some songs to fit this {} day. It is {} degrees Celsius in {}".format(self.weather, self.temp, self.location),
            "public": True
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        response_json = response.json()
        #playlist id
        self.playlist_link = response_json["external_urls"]["spotify"]
        return response_json["id"]

    # Gets size of user's library
    def get_library_size(self):
        query = "https://api.spotify.com/v1/me/tracks?limit=1"
        page_response = requests.get(
            query,
            headers={
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )

        response_json = page_response.json()
        
        total = response_json["total"]
    
        return total

    # Get the URI of the given song by the given artist
    def get_spotify_uri(self, song_name, artist):

        query = "https://api.spotify.com/v1/search?q=track%3A{}%20artist%3A{}&type=track".format(song_name, artist)

        uri_response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )

        response_json = uri_response.json()
        songs = response_json["tracks"]["items"]
        uri = songs[0]["uri"]

        return uri

    # Gets 20 songs that fit the weather
    # Adds the songs to our newly created empty playlist
    def add_songs_to_playlist(self):
        # create playlist
        playlist_id = self.create_playlist()
        selection_size = self.get_library_size() - 1
        uris = self.get_random_songs_from_library(selection_size)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

        uri_data = json.dumps(uris)

        add_response = requests.post(
            query,
            data=uri_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token),
            }
        )

        # check for valid response status
        if add_response.status_code != 201:
            raise ResponseException(add_response.status_code)

        response_json = add_response.json()
        return response_json

    # Pulls random songs from user's Spotify library until we have 20
    # Checks if the song fits with the weather
    # Adds to list if so, rejects and moves on if not
    def get_random_songs_from_library(self, selection_size):
        song_list = []
        prev = []

        i = 0
        while i < 20:
            offset = random.randrange(0, selection_size)
            while offset in prev:
                offset = random.randrange(0, selection_size)
            prev.append(offset)

            query = "https://api.spotify.com/v1/me/tracks?limit=1&offset={}".format(offset)

            get_response = requests.get(
                query,
                headers={
                    "Authorization": "Bearer {}".format(self.spotify_token)
                }
            )

            if get_response.status_code != 200:
                raise ResponseException(get_response.status_code)

            response_json = get_response.json()
            songs = response_json["items"]
            song = songs[0]['track']['uri']

            song_id = song[14::]

            feature_query = "https://api.spotify.com/v1/audio-features/{}".format(song_id)

            feature_response = requests.get(
                feature_query,
                headers={
                    "Authorization": "Bearer {}".format(self.spotify_token)
                }
            )

            feature_response_json = feature_response.json()

            if not self.weather_corr[self.weather](feature_response_json, self.temp):
                continue

            song_list.append(songs[0]['track']['uri'])

            i += 1
            print(i, "songs added")

        return song_list
    
    def get_playlist_link(self):
        return self.playlist_link

# Check if song is energetic and good for dancing
def is_sunny(response_json, temp):
    valence = response_json["valence"]
    danceability = response_json["danceability"]

    if temp >= 25:
        return valence > 0.5 and danceability < 0.5
    elif temp >= 9:
        return valence > 0.5 and danceability >= 0.5
    else:
        return valence > 0.35 and danceability <= 0.6

# Check if song is slower, but not horribly sad
def is_cloudy(response_json, temp):
    valence = response_json["valence"]
    danceability = response_json["danceability"]

    if temp >= 25:
        return valence < 0.5 and danceability < 0.5
    elif temp >= 9:
        return valence < 0.5 and danceability >= 0.5
    else:
        return valence < 0.5 and danceability < 0.3

# Check that song is low energy, not meant to boost anyone's mood
def is_rainy(response_json, temp):
    valence = response_json["valence"]
    energy = response_json["energy"]

    return valence < 0.4 and energy < 0.4


#if __name__ == '__main__':
#    skies = input("What's the weather like today? ")
#    temperature = input("How hot is it? ")
#    #cp = CreatePlaylist(skies, temperature)
#    if skies == "rainy":
#        pickmeup = input("Do you need a pick me up? y/n ")
#        if pickmeup == "y":
#            weather = "sunny"

#    saved_num = int(input("How many songs do you have saved? "))
    #cp.add_songs_to_playlist(saved_num)
#    print("Done")

