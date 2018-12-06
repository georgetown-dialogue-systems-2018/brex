import logging
import random

from brex.handlers.handler import Handler
import brex.goodreads as gr

# def author(author_id):
# def find_author(author_name):
# def book(book_id=None, isbn=None):
# def search_books(q, page=1, search_field='all'):
# def review(review_id):

filtering_entities = ['']
generating_entities = ['author', 'author_like', 'title_like']

class Inform(Handler):
    def __init__(self):
        self._already_recommended = set()
        self._latest_books = None
        self._latest_search_params = None

    # generating functions
    def _generate_by_author(self, context, authors):

        # just take the most likely one for now
        author_name = authors[0]['value']
        books = gr.search_books(author_name, page=1, search_field='author')
        self._latest_search_params = (author_name, 1, 'author')

        if books:
            logging.debug('Found books for author "{}": {}'.format(author_name, str(books)))
            return {'books': books}
        else:
            logging.debug('Failed to find any books for author "{}"'.format(author_name))
            return {'failure': 'none_found_by_author'}

    def _generate_books(self, context, wit_response):
        for name, vals in wit_response['entities'].items():
            # choose the first one
            if name in generating_entities:
                logging.debug('Generating intents based on slot "{}"'.format(name))
                return (self._generate_by_author(context, vals) if name == 'author' else
                        None if name == 'author_like' else
                        None)
        logging.debug('Tried to generate books, but not generating entities were detected.')
        logging.debug('Attempting to suggest one from the list, if present')
        return self._handle_reject(context, wit_response, called_from_generate=True)

    # filtering functions
    def _filter_books(self, context, wit_response, books):
        return {'books': [book for book in books if book not in self._already_recommended]}

    # handling functions
    def _select_book(self, context, wit_response, books):
        book = books[0]

        # keep track of this in case we need to recommend another
        self._already_recommended.add(book)
        self._latest_books = books[1:]

        # let other handlers know
        context['current_book'] = book
        logging.debug('Recommending book "{}". {} books remain'
                      .format(book, len(self._latest_books)))
        return {'book': book}

    def _handle_reject(self, context, wit_response, called_from_generate=False):
        if len(self._latest_books) > 0:
            return self._select_book(context, wit_response, self._latest_books)
        else:
            q, page, field = self._latest_search_params
            self._latest_search_params = (q, page + 1, field)
            books = gr.search_books(q, page + 1, field)

            if books:
                return self.select_book(context, wit_response, books)
            elif not called_from_generate:
                return {'failure': 'book_list_exhausted'}
            else:
                return {'failure': 'no_generating_entities'}

    def _handle_query(self, context, wit_response):
        books_query = self._generate_books(context, wit_response)
        if 'failure' in books_query:
            return books_query

        books_query = self._filter_books(context, wit_response, books_query['books'])
        if 'failure' in books_query:
            return books_query

        return self._select_book(context, wit_response, books_query['books'])

    # text generation functions
    def _generate_text(self, context, wit_response, system_intent):
        if 'failure' in system_intent:
            return system_intent['failure']
        elif 'book' in system_intent:
            return 'Have you read "{}"?'.format(system_intent['book'])
        else:
            raise Exception("""Tried to generate text for the intent 'inform', but didn't
recognize any system intents.\n\n{}""".format(str(system_intent)))

    # top level function called by the manager
    def handle(self, context, wit_response):
        output = {}

        entities = wit_response['entities']
        if 'reject' in entities:
            system_intent = self._handle_reject(context, wit_response)
        else:
            system_intent = self._handle_query(context, wit_response)

        output['text'] = self._generate_text(context, wit_response, system_intent)
        return output




