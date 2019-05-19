import os
import logging
from datetime import datetime
import pprint
import traceback

from wit import Wit
from flask_socketio import Namespace, emit
import brex.config as cfg
from brex.common import import_python_file


def snake2title(s):
    return "".join([w.capitalize() for w in s.split('_')])

class WitManager(Namespace):
    def __init__(self, namespace='/'):
        # Namespace is a superclass we need to inherit from for socket.io
        # Come to think of it, this should probably be living in the driver
        # instead of the manager...
        super().__init__(namespace)

        # Wit is a wrapper for the wit.ai HTTP API
        self._wit_client = Wit(cfg.wit_access_token)

        # str -> instance of Handler, which handles a single value of the
        #   wit.ai entity `intent`
        self._handlers = {}

        # history -> list of objs with keys `wit` and `handler`, corresponding
        #   to the wit HTTP API's output JSON and the handler's output dict in
        #   response to the wit JSON.
        # current_book -> goodreads book object for the book that is currently
        #   being suggested. This correctly suggests that this system is limited
        #   to only discussing a single book at a time, rather than a set of books.
        self._context = {}

        self.reset()

    def reset(self):
        """Called at instantiation and at the end of a conversation by a Driver to
        reset WitManager's internal state."""
        self._context = {'history': [],
                         'current_book': None}
        # handlers might have had internal state--reinstantiate
        self._load_handlers()

    def _load_handlers(self):
        "Load (almost) all Python classes in the 'handlers/' directory and instantiate"
        self._handlers = {}

        basedir = os.sep.join(['brex', 'handlers'])
        filenames = [filename
                     for filename in os.listdir(basedir)
                     if filename is not 'handler.py'
                        and not filename.startswith('_')
                        and not filename.startswith('.')]

        for fname in filenames:
            handler_name = fname[:-3]
            handler_module = import_python_file(basedir + os.sep + fname)
            handler_class = getattr(handler_module, snake2title(handler_name))

            self._handlers[handler_name] = handler_class()

        logging.debug('Loaded wit handlers: %s', self._handlers)

    def _choose_handler(self, wit_resp):
        "Find a handler to hand off execution to given the intent reported by Wit"
        try:
            most_likely_intent = wit_resp['entities']['intent'][0]['value']
            logging.debug('Most likely intent: ' + most_likely_intent)

            return self._handlers[most_likely_intent]
        except KeyError as e:
            logging.error('''Either the response from Wit didn't have an intent,
or there was no handler for the intent.''')
            logging.error(traceback.format_exc())

        if cfg.debug:
            return self._handlers['echo']
        else:
            # TODO: use something else that will try to change topic or something
            return self._handlers['echo']

    def respond(self, user_input):
        """Take user input and return a dict instructing the driver on how to
        behave:
          - text: the system's output
          - suggestions: optional, a list of input suggestions the driver should
                         display for the user. Drivers may choose not to implement
                         display of suggestions.
          - exit: optional, driver should exit if it is present and truthy"""
        logging.debug("Received user input: '%s'", user_input)

        wit_response = self._wit_client.message(user_input)
        logging.debug("Received response from Wit: %s", str(wit_response))

        handler = self._choose_handler(wit_response)
        logging.debug("Selected handler %s", str(handler))

        handler_response = handler.handle(self._context, wit_response)

        self._context['history'].append({'wit': wit_response,
                                         'handler': handler_response})

        logging.debug("Responding: %s", str(handler_response))
        return handler_response


    def _log_convo(self):
        logdir = cfg.convo_logging_dir
        if logdir:
            if not os.path.exists(logdir):
                os.mkdir(logdir, 0o700)

            filename = datetime.now().strftime("%y-%m-%d_%H:%M.%f")
            history = self._context['history']

            with open(logdir + os.sep + filename + ".py", 'w') as f:
                f.write(pprint.pformat(history) + "\n")
            with open(logdir + os.sep + filename + ".txt", 'w') as f:
                lines = []
                for pair in history:
                    lines.append("User:\t" + pair['wit']['_text'])
                    lines.append("Brex:\t" + pair['handler']['text'])
                f.write("\n".join(lines) + "\n")

    # Flask SocketIO methods
    def on_connect(self):
        pass

    def on_disconnect(self):
        self._log_convo()

    def on_user_message(self, data):
        message = data['message']

        try:
            response = self.respond(message)
        except Exception as e:
            logging.error("Encountered an error while attempting to respond.")
            logging.error(traceback.format_exc())
            response = {'text': 'Sorry, I think I dozed off--what was that?'}
        should_exit = response['exit'] if 'exit' in response else False
        socket_data = {'message': response['text'],
                       'suggestions': response['suggestions'] if 'suggestions' in response else None,
                       'exit': should_exit}
        emit('brex_message', socket_data)

        if should_exit:
            self._log_convo()
            self.reset()
