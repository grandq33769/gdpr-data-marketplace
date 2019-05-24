from server import app, socketio
app.config.from_object('config.dev')

if __name__ == '__main__':
   socketio.run(app, host=app.config['HOST'], port=app.config['PORT'])