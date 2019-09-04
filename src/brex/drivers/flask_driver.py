from flask import Flask, request, render_template, send_from_directory
from flask_socketio import SocketIO, send, emit, Namespace
import traceback
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

        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/static/<path:path>')
        def send_static(path):
            return send_from_directory('static', path)

        socketio.on_namespace(SessionManager(self._dm_class))
        socketio.run(app, host=cfg.flask_host, port=cfg.flask_port, debug=cfg.debug)


class SessionManager(Namespace):
    def __init__(self, dm_class, namespace='/'):
        # Namespace is a superclass we need to inherit from for socket.io
        super().__init__(namespace)
        self._dm_class = dm_class
        self._managers = {}

    # Flask SocketIO methods
    def on_connect(self):
        logging.info(f"Session {request.sid} begun.")
        self._managers[request.sid] = self._dm_class()

    def on_disconnect(self):
        logging.info(f"Session {request.sid} ended.")
        self._managers[request.sid].log_convo()
        del self._managers[request.sid]

    def on_user_message(self, data):
        message = data['message']

        try:
            response = self._managers[request.sid].respond(message)
        except Exception as e:
            logging.error("Encountered an error while attempting to respond.")
            logging.error(traceback.format_exc())
            response = {'text': 'Sorry, I think I dozed off--what was that?'}
        should_exit = response['exit'] if 'exit' in response else False
        socket_data = {'message': response['text'],
                       'suggestions': response['suggestions'] if 'suggestions' in response else None,
                       'exit': should_exit}
        emit('brex_message', socket_data, room=request.sid)

        if should_exit:
            self._managers[request.sid].log_convo()
            self._managers[request.sid].reset()