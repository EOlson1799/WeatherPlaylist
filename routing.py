from flask import Flask, request, render_template
from .create_playlist import CreatePlaylist
from .secrets import weather_key
import requests

app = Flask(__name__)
app.debug = True

# Uses given city and country (State is optional) to find weather conditions
# via WeatherBit.io API
def get_weather(city, country, state=None):
    if state:
        query = "https://api.weatherbit.io/v2.0/current?city={},{}&country={}&key={}".format(city, state, country, weather_key)
    else:
        query = "https://api.weatherbit.io/v2.0/current?city={}&country={}&key={}".format(city, country, weather_key)
    
    weather_request = requests.get(query)

    weather_json = weather_request.json()
    print(weather_json)

    data = weather_json['data'][0]

    weather_code = data['weather']['code']
    temp = data['temp']

    return weather_code, temp


#@app.route('/playlist')
#def create():
#    create_p = CreatePlaylist("sunny", "cool")
#    create_p.add_songs_to_playlist(1811)
#    return 'Check ur spotify loser'

# Testing
@app.route('/form')
def my_form():
    return render_template('myform.html')

# Main route, gets location for weather conditions
# Creates Playlist object and returns link to web page
@app.route('/', methods=['GET', 'POST'])
def my_form_post():
    if request.method == 'GET':
        return render_template('myform.html')
    
    elif request.method == 'POST':
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        
        if state:
            location = city + ", " + state +  ", " + country
        else:
            location = city + ", " + country
        
        weather_code, temp = get_weather(request.form["city"], state=request.form["state"], country=request.form["country"])
        create_p = CreatePlaylist(weather_code, temp, location)
        create_p.add_songs_to_playlist()
        link = create_p.get_playlist_link()
    
    return render_template("link.html", playlist_link=link)
