from goodreads import client
from diskcache import FanoutCache

import brex.config as cfg

# global state... might not quite work with multiple concurrent users
CLIENT = client.GoodreadsClient(cfg.gr_api_key, cfg.gr_api_secret)
CACHE = FanoutCache('../__goodreads_cache__')

# wrapped functions from the GoodreadsClient
# cf https://github.com/sefakilic/goodreads/blob/master/goodreads/client.py

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
    return CLIENT.search_books(q, page=page, search_field=search_field)
