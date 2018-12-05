from brex.managers.wit.handlers.handler import Handler

class Bye(Handler):
    def __init__(self):
        pass

    def handle(self, context, wit_response):
        output = {}
        output['text'] = 'So long!'
        output['exit'] = True
        return output
