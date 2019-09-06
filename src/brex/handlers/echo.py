import logging

from brex.handlers.handler import Handler
from brex.config import debug

class Echo(Handler):
    def __init__(self):
        pass

    def handle(self, context, wit_response):
        output = {}

        if debug:
            logging.error("No handler found for this intent! Echoing the JSON back at you:")
            output['text'] = str(wit_response)
        else:
            output['text'] = 'Sorry, I don\'t quite understand. Could you say that again?'
        output['exit'] = False

        return output
