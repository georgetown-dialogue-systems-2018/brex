import types
import collections
from goodreads import client
from diskcache import FanoutCache

import brex.config as cfg

# modify the class so we don't eagerly fetch info for every book
class LazyGoodreadsClient(client.GoodreadsClient):
    def search_index(self, q, page, search_field):
        return self.request("search/index.xml",
                              {'q': q, 'page': page, 'search[field]': search_field})

    # returns IDs instead of full book objects as the original version does
    def search_books(self, q, page=1, search_field='all'):
        resp = self.search_index(q, page, search_field)
        works = resp['search']['results']['work']
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
    return CLIENT.search_books(q, page=page, search_field=search_field)


