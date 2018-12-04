import abc

class Manager(object):
    def __init__(self):
        pass

    @abc.abstractmethod
    def respond(self, user_input):
        # output should be a dict with at least two keys: 'text': str, 'exit': bool
        pass
