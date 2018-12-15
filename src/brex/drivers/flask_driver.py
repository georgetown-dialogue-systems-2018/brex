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

        socketio.on_namespace(self._dm_class('/'))
        socketio.run(app, host=cfg.flask_host, port=cfg.flask_port, debug=cfg.debug)
