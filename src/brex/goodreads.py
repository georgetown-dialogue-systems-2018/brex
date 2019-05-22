import types
import logging
import collections
from goodreads import client
from diskcache import FanoutCache
from lxml.html import fromstring
import requests

import brex.config as cfg

# modify the class so we don't eagerly fetch info for every book
class LazyGoodreadsClient(client.GoodreadsClient):
    def search_index(self, q, page, search_field):
        return self.request("search/index.xml",
                              {'q': q, 'page': page, 'search[field]': search_field})

    # returns IDs instead of full book objects as the original version does
    def search_books(self, q, page=1, search_field='all'):
        resp = self.search_index(q, page, search_field)
        try:
            works = resp['search']['results']['work']
        except TypeError:
            works = []

        # If there's only one work returned, put it in a list.
        if type(works) == collections.OrderedDict:
            works = [works]

        return [work['best_book']['id']['#text'] for work in works]


# global state... might not quite work with multiple concurrent users
CLIENT = LazyGoodreadsClient(cfg.gr_api_key, cfg.gr_api_secret)
CACHE = FanoutCache('../__goodreads_cache__')

# wrapped functions with caching from the GoodreadsClient
@CACHE.memoize(expire=86400)
def author(author_id):
    return CLIENT.author(author_id)

@CACHE.memoize(expire=86400)
def find_author(author_name):
    return CLIENT.find_author(author_name)

@CACHE.memoize(expire=86400)
def book(book_id=None, isbn=None):
    return CLIENT.book(book_id=book_id, isbn=isbn)

@CACHE.memoize(expire=86400)
def search_books(q, page=1, search_field='all'):
    results = CLIENT.search_books(q, page=page, search_field=search_field)
    logging.debug("search_books returning: %s", results)
    return results

@CACHE.memoize(expire=86400)
def reviews(book_id):
    r = requests.get('https://www.goodreads.com/book/show/' + str(book_id))
    parsed_html = fromstring(r.text)
    containers = parsed_html.xpath('//*[starts-with(@id, "reviewTextContainer")]')

    full_reviews = []
    for container in containers:
        try:
            full_review = container.xpath('./span[position() = 2]')[0]
        except IndexError:
            full_review = container.xpath('./span[position() = 1]')[0]
        full_reviews.append(full_review)

    return [review.text_content() for review in full_reviews]
