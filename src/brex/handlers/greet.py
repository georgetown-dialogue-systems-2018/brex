from brex.handlers.handler import Handler

class Greet(Handler):
    def __init__(self):
        pass

    def handle(self, context, wit_response):
        output = {}
        output['text'] = 'Hi, my name\'s B. Rex! Why don\'t you tell me about your favorite kind of book?'
        output['suggestions'] = ["I want a fantasy novel", "I like Stephen King"]
        return output
