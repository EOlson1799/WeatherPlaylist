from flask import Flask, request, render_template
from .create_playlist import CreatePlaylist

app = Flask(__name__)
app.debug = True

@app.route('/playlist')
def create():
    create_p = CreatePlaylist("sunny", "cool")
    create_p.add_songs_to_playlist(1811)
    return 'Check ur spotify loser'


@app.route('/form')
def my_form():
    return render_template('myform.html')


@app.route('/form', methods=['GET', 'POST'])
def my_form_post():
    if request.method == 'GET':
        return render_template('myform.html')
    elif request.method == 'POST':
        weather = request.form["weather"]
        temp = request.form["temp"]
        create_p = CreatePlaylist(weather.lower(), temp.lower())
        # this number should be the amount of songs in your library
        create_p.add_songs_to_playlist(1811)
    return 'Check ur spotify, loser'
