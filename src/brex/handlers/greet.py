from brex.handlers.handler import Handler

class Greet(Handler):
    def __init__(self):
        pass

    def handle(self, context, wit_response):
        output = {}
        output['text'] = 'Hi, my name\'s B. Rex!'
        return output