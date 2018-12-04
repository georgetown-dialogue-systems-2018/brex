import abc

class Driver(object):
    def __init__(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass
