import os
import importlib
import logging

from wit import Wit
from flask_socketio import Namespace, emit
import brex.config as cfg


def snake2title(s):
    return "".join([w.capitalize() for w in s.split('_')])

class WitManager(Namespace):
    def __init__(self, namespace):
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
            fname = fname[:-3]   # strip '.py'
            intent_name = fname

            fpath = basedir + os.sep + fname
            fpath = fpath.replace(os.sep, '.')

            handler_module = importlib.import_module(fpath)
            handler_class = getattr(handler_module, snake2title(fname))

            self._handlers[intent_name] = handler_class()

        logging.debug('Loaded wit handlers: {}'.format(str(self._handlers)))

    def _choose_handler(self, wit_resp):
        "Find a handler to hand off execution to given the intent reported by Wit"
        try:
            most_likely_intent = wit_resp['entities']['intent'][0]['value']
            logging.debug('Most likely intent: ' + most_likely_intent)

            return self._handlers[most_likely_intent]
        except KeyError as e:
            logging.debug('''Either the response from Wit didn't have an intent,
or there was no handler for the intent.''')

        if cfg.debug:
            return self._handlers['echo']
        else:
            # todo: use something else that will try to change topic or something
            return self._handlers['echo']

    def respond(self, user_input):
        """Take user input and return a dict instructing the driver on how to
        behave:
          - text: the system's output
          - exit: optional, driver should exit if it is present and truthy"""
        output = {}
        logging.debug("Received user input: '{}'".format(user_input))

        wit_response = self._wit_client.message(user_input)
        logging.debug("Received response from Wit: {}".format(str(wit_response)))

        handler = self._choose_handler(wit_response)
        logging.debug("Selected handler {}".format(str(handler)))

        handler_response = handler.handle(self._context, wit_response)

        self._context['history'].append({'wit': wit_response,
                                         'handler': handler_response})

        return handler_response


    # Flask SocketIO methods
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_user_message(self, data):
        message = data['message']

        try:
            response = self.respond(message)
        except Exception as e:
            logging.error("Encountered an error while attempting to respond. Error: {}".format(e))
            response = {'text': 'Sorry, I think I dozed off--what was that?'}
        should_exit = response['exit'] if 'exit' in response else False
        socket_data = {'message': response['text'], 'exit': should_exit}
        emit('brex_message', socket_data)

        if should_exit:
            self.reset()


