import logging
from random import choice

from brex.handlers.handler import Handler
import brex.goodreads as gr
#from brex.template_renderer import TemplateRenderer

filtering_entities = ['']
generating_entities = ['author', 'genre']

class Personal(Handler):
    def __init__(self):
        pass

    def _handle_favorite_book(self, context, wit_response):
        s = ""
        return s

    def _handle_genre(self, context, wit_response):
        s = ""
        return s

    def _handle_name(self, context, wit_response):
        s = ""
        return s

    def _handle_residence(self, context, wit_response):
        s = ""
        return s

    def _handle_reality(self, context, wit_response):
        s = ""
        return s

    def _handle_age(self, context, wit_response):
        s = ""
        return s

    def _handle_fallback(self, context, wit_response):
        handler = choice([self._handle_favorite_book,
                          self._handle_genre,
                          self._handle_name,
                          self._handle_residence,
                          self._handle_reality,
                          self._handle_age])
        return handler(context, wit_response)

    # top level function called by the manager
    def handle(self, context, wit_response):
        output = {}

        entities = wit_response['entities']

        if 'favorite_book' in entities:
            output['text'] = self._handle_favorite_book(context, wit_response)
        elif 'genre' in entities:
            output['text'] = self._handle_genre(context, wit_response)
        elif 'name' in entities:
            output['text'] = self._handle_name(context, wit_response)
        elif 'residence' in entities:
            output['text'] = self._handle_residence(context, wit_response)
        elif 'reality' in entities:
            output['text'] = self._handle_reality(context, wit_response)
        elif 'age' in entities:
            output['text'] = self._handle_age(context, wit_response)
        else:
            output['text'] = self._handle_fallback(context, wit_response)

        output['text'] = self._generate_text(context, wit_response, system_intent)
        return output
