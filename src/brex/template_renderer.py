from random import choice
from functools import reduce
from operator import getitem
import os
import toml

class TemplateRenderer():
    def __init__(self, filename):
        self._data = toml.load(os.sep.join(['brex', 'templates', filename + '.toml']))

    def render(self, kind, keywords={}, strategy="random"):
        keys = kind.split(".")
        templates = reduce(getitem, keys, self._data)

        if strategy == "random":
            return choice(templates).format(**keywords)
        else:
            raise Exception("Unknown strategy '{}'".format(strategy))

