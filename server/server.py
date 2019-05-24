from flask import render_template
from flask_socketio import emit
from server import app, socketio


@app.route('/')
def index():
   return render_template('index.html')


@socketio.on('my event', namespace='/test')
def test_message(message):
   emit('my response', {'data': message['data']})


@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
   emit('my response', {'data': message['data']}, broadcast=True)


@socketio.on('connect', namespace='/test')
def test_connect():
   emit('my response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
   print('Client disconnected')



