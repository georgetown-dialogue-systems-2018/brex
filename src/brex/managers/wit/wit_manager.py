import os
import importlib
import logging

from wit import Wit

from brex.managers.manager import Manager
import brex.config as cfg

def snake2title(s):
    return "".join([w.capitalize() for w in s.split('_')])

class WitManager(Manager):

    def __init__(self):
        self._wit_client = Wit(cfg.wit_access_token)
        self._wit_handlers = {}
        self._context = {}
        self._load_handlers()

    def _load_handlers(self):
        basedir = os.sep.join(['brex', 'managers', 'wit', 'handlers'])
        filenames = [filename
                     for filename in os.listdir(basedir)
                     if filename is not 'handler.py'
                        and not filename.startswith('_')
                        and not filename.startswith('.')]

        for fname in filenames:
            fname = fname[:-3] # strip .py
            intent_name = fname

            fpath = basedir + os.sep + fname
            fpath = fpath.replace(os.sep, '.')

            print(fpath)
            handler_module = importlib.import_module(fpath)
            handler_class = getattr(handler_module, snake2title(fname))

            self._wit_handlers[intent_name] = handler_class()

        logging.debug('Loaded wit handlers: {}'.format(str(self._wit_handlers)))

    def _choose_handler(self, wit_resp):
        try:
            most_likely_intent = wit_resp['entities']['intent'][0]['value']
            logging.debug('Most likely intent: ' + most_likely_intent)
            if most_likely_intent in self._wit_handlers:
                return self._wit_handlers[most_likely_intent]
        except:
            logging.debug('It looks like the response from Wit didn\'t have an intent.')
        return self._wit_handlers['echo']

    def respond(self, user_input):
        output = {}
        logging.debug("Received user input: '{}'".format(user_input))

        wit_response = self._wit_client.message(user_input)
        logging.debug("Received response from Wit: {}".format(str(wit_response)))

        handler = self._choose_handler(wit_response)
        logging.debug("Selected handler {}".format(str(handler)))

        return handler.handle(self._context, wit_response)
