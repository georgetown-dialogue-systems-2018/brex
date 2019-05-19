from random import choice
from functools import reduce
from operator import getitem
import os

from brex.common import import_python_file

class TemplateRenderer():
    def __init__(self, filename):
        pyfile = import_python_file(
            os.sep.join(['brex', 'templates', filename + '.py']))

        self._data = getattr(pyfile, filename)
        self._linear_counter = 0

    def render(self, kind, keywords={}, strategy="random"):
        keys = kind.split(".")
        templates = reduce(getitem, keys, self._data)

        if strategy == "random":
            template = choice(templates)
        elif strategy == "linear":
            template = templates[self._linear_counter % len(templates)]
            self._linear_counter += 1
        else:
            raise Exception("Unknown strategy '{}'".format(strategy))

        template['text'] = template['text'].format(**keywords)
        return template
