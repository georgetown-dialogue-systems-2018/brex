from random import choice
class Choice():
    def __init__(self, opts):
        self._opts = opts

    def select(self, strategy="random"):
        if strategy == "random":
            return choice(self._opts)
        else:
            raise Exception("Unknown strategy '{}'".format(strategy))

