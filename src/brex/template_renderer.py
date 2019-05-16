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

    def render(self, kind, keywords={}, strategy="random"):
        keys = kind.split(".")
        templates = reduce(getitem, keys, self._data)

        if strategy == "random":
            return choice(templates).format(**keywords)
        else:
            raise Exception("Unknown strategy '{}'".format(strategy))
