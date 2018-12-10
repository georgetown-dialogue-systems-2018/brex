from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, send, emit
import os
import logging

from brex.drivers.driver import Driver
import brex.config as cfg

class FlaskDriver(Driver):
    def __init__(self, dm_class):
        self._dm_class = dm_class

    def run(self):
        app = Flask(__name__, template_folder='flask_templates')
        app.config['SECRET_KEY'] = cfg.flask_secret
        socketio = SocketIO(app)

        sessions = {}

        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/static/<path:path>')
        def send_static(path):
            return send_from_directory('static', path)

        @socketio.on('user-connected')
        def user_connected(data):
            print("connected")
            sessions[data['session']] = self._dm_class()

        @socketio.on('user-disconnected')
        def user_disconnected(data):
            del sessions[data['session']]

        @socketio.on('user-message')
        def test_message(data):
            print(data)
            session = data['session']
            message = data['message']

            try:
                response = sessions[session].respond(message)
            except Exception as e:
                logging.error("Encountered an error while attempting to respond. Error: {}".format(e))
                response = {'text': 'Sorry, I think I dozed off--what was that?'}
            should_exit = response['exit'] if 'exit' in response else False
            socket_data = {'message': response['text'], 'exit': should_exit}
            emit('brex-message', socket_data)

            if should_exit:
                sessions[session].reset()

        socketio.run(app, host=cfg.flask_host, port=cfg.flask_port, debug=cfg.debug)
