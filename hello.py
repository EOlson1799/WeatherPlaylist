from flask import Flask, request, render_template
from .create_playlist import CreatePlaylist

app = Flask(__name__)
app.debug = True

<<<<<<< HEAD

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/shh')
def shut_up():
    return 'Shut the fuck up'


=======
>>>>>>> 586577bcdc094ac9d8c0227440bdf5c72f25bb56
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
