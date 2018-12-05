import logging
import random

from brex.managers.wit.handlers.handler import Handler
import brex.goodreads as gr

# def author(author_id):
# def find_author(author_name):
# def book(book_id=None, isbn=None):
# def search_books(q, page=1, search_field='all'):
# def review(review_id):

class Inform(Handler):
    def __init__(self):
        pass

    def _find_book_by_author_fail(self, context, author):
        return "I couldn't find an author by that name. Can you think of another?"

    def _find_book_by_author_success(self, context, book):
        context['current_book'] = book
        return "I found a book called {}".format(book.title)

    def _find_book_by_author(self, context, author_name):
        "Propose a book by the author"
        author_obj = gr.find_author(author_name)
        logging.debug("Author object found: " + str(author_obj))
        if not author_obj:
            return self._find_book_by_author_fail(context, author_name)

        return self._find_book_by_author_success(context, random.choice(author_obj.books))

    def handle(self, context, wit_response):
        output = {}

        entities = wit_response['entities']
        author = entities['author'][0]['value'] if 'author' in entities else None

        output['text'] =  self._find_book_by_author(context, author)
        return output
