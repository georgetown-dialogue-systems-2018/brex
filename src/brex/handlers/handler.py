import abc

class Handler(object):
    def __init__(self):
        pass

    @abc.abstractmethod
    def handle(self, context, wit_response):
        pass
