import logging

import brex.config as cfg
from brex.handlers.handler import Handler
import brex.goodreads as gr
from brex.template_renderer import TemplateRenderer
import brex.templates.inform as inform_templates

filtering_entities = ['']
generating_entities = ['author', 'genre']

class Inform(Handler):
    def __init__(self):
        self._already_recommended = set()
        self._latest_books = []
        self._latest_search_params = None

        self._renderer = TemplateRenderer('inform')

    # generating functions
    def _generate_by_author(self, context, authors):

        # just take the most likely one for now
        author_name = authors[0]['value']
        books = gr.search_books(author_name, page=1, search_field='author')
        self._latest_search_params = (author_name, 1, 'author')

        if books:
            logging.debug('Found books for author "{}": {}'.format(author_name, str(books)))
            return {'books': books,
                    'author': author_name}
        else:
            logging.debug('Failed to find any books for author "{}"'.format(author_name))
            return {'failure': 'none_found_by_author',
                    'author': author_name}

    def _generate_by_genre(self, context, genre):

        # just take the most likely one for now
        genre_name = genre[0]['value']
        books = gr.search_books(genre_name, page=1, search_field='genre')
        self._latest_search_params = (genre_name, 1, 'genre')

        if books:
            logging.debug('Found books for genre "{}": {}'.format(genre_name, str(books)))
            return {'books': books,
                    'genre': genre_name}
        else:
            logging.debug('Failed to find any books for genre "{}"'.format(genre_name))
            return {'failure': 'none_found_by_genre',
                    'genre': genre_name}

    def _generate_books(self, context, wit_response):
        for name, vals in wit_response['entities'].items():
            # choose the first one
            if name in generating_entities:
                logging.debug('Generating intents based on slot "{}"'.format(name))
                if name == "author":
                    return self._generate_by_author(context, vals)
                elif name == "genre":
                    return self._generate_by_genre(context, vals)
                else:
                    return None
        logging.debug('Tried to generate books, but not generating entities were detected.')
        logging.debug('Attempting to suggest one from the list, if present')
        return self._handle_reject(context, wit_response, called_from_generate=True)

    # filtering functions
    def _filter_books(self, context, wit_response, books):
        return {'books': [book for book in books if book not in self._already_recommended]}

    # handling functions
    def _select_book(self, context, wit_response, books):
        # keep track of this in case we need to recommend another
        self._already_recommended.add(books[0])
        self._latest_books = books[1:]

        # call the function to actually retrieve the info
        book = gr.book(books[0])

        # let other handlers know
        context['current_book'] = book
        logging.debug('Recommending book "{}". {} books remain'
                      .format(book, len(self._latest_books)))
        return {'book': book}

    def _handle_reject(self, context, wit_response, called_from_generate=False):
        if len(self._latest_books) > 0:
            return self._select_book(context, wit_response, self._latest_books)
        else:
            if not self._latest_search_params:
                return {'failure': 'no_generating_entities'}

            q, page, field = self._latest_search_params
            self._latest_search_params = (q, page + 1, field)
            books = gr.search_books(q, page + 1, field)

            if books:
                return self._select_book(context, wit_response, books)
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

    def _generate_failure_response(self, context, wit_response, system_intent):
        reason = system_intent['failure']
        if reason == 'none_found_by_author':
            author = system_intent['author']
            return self._renderer.render('none_found_by_author',
                                         {'author': author},
                                         strategy=cfg.template_selection_strategy)
        elif reason == 'none_found_by_genre':
            genre = system_intent['genre']
            return self._renderer.render('none_found_by_genre',
                                         {'genre': genre},
                                         strategy=cfg.template_selection_strategy)
        elif reason == 'book_list_exhausted':
            return self._renderer.render('book_list_exhausted',
                                         strategy=cfg.template_selection_strategy)
        elif reason == 'no_generating_entities':
            return self._renderer.render('no_generating_entities',
                                         strategy=cfg.template_selection_strategy)
        else:
            raise Exception('Tried to generate text for unknown failure "{}"'.format(reason))

    def _generate_book_response(self, context, wit_response, system_intent):
        book = context['current_book']
        gid = int(book.gid)
        book = '<a href="https://www.goodreads.com/book/show/' + book.gid + '">' + book.title + '</a>'
        response = self._renderer.render('book', {'book': book}, strategy=cfg.template_selection_strategy)
        if gid in inform_templates.flavor:
            response['text'] += " " + inform_templates.flavor[gid]
        return response

    # response generation functions
    def _generate_response(self, context, wit_response, system_intent):
        if 'failure' in system_intent:
            return self._generate_failure_response(context, wit_response, system_intent)
        elif 'book' in system_intent:
            return self._generate_book_response(context, wit_response, system_intent)
        else:
            raise Exception("""Tried to generate text for the intent 'inform', but didn't
recognize any system intents.\n\n{}""".format(str(system_intent)))

    # top level function called by the manager
    def handle(self, context, wit_response):
        entities = wit_response['entities']
        if 'reject' in entities:
            system_intent = self._handle_reject(context, wit_response)
        else:
            system_intent = self._handle_query(context, wit_response)

        output = self._generate_response(context, wit_response, system_intent)
        output['text'] = output['text'][0].capitalize() + output['text'][1:]
        return output
