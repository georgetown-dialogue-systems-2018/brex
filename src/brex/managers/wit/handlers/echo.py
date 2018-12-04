import logging

from brex.managers.wit.handlers.handler import Handler
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
            output['text'] = str(wit_response['_text'])
        output['exit'] = False

        return output
