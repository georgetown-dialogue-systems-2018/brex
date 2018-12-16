import logging
from random import choice

from brex.handlers.handler import Handler
import brex.goodreads as gr
#from brex.template_renderer import TemplateRenderer

filtering_entities = ['']
generating_entities = ['author', 'genre']

class Personal(Handler):
    def __init__(self):
        pass

    def _handle_favorite_book(self, context, wit_response):
        context['current_book'] = gr.book('18839')
        s = "I have my mind less made up about genres, but when it comes to the books I've enjoyed most, there's only one that makes it to the top. That book is <a href=\"https://www.goodreads.com/book/show/18839\">'Orlando' by Virginia Woolf</a>, if you've heard of it. The main character, Orlando, lives for 300 years and has to grapple with the anachronism of his own existence. My father picked it out for me while I was still a teen in the lab, and I know why. It's because he must have understood my own bewilderment at being a genetically enhanced Tyrannosaurus rex in the modern day. As you can probably tell already from how long I've gone on about it, it resonated with me."
        return s

    def _handle_genre(self, context, wit_response):
        s = "Perhaps it's better to ask what genre I don't like! Horror doesn't do much for me, and while I enjoy detective novels, I feel that the suspense often comes at the expense of the character development."
        return s

    def _handle_name(self, context, wit_response):
        s = "Yes, what's the 'B' stand for? Don't worry, I get it all the time. It's Bruce. My dad really likes Bruce Springsteen."
        return s

    def _handle_residence(self, context, wit_response):
        s = "I live with my dad in the rolling green hills of Appalachia. Nothing's better than waking up on a misty Saturday morning and watching the mountains peek out at you through the haze while you're curled up with a book in the solarium."
        return s

    def _handle_reality(self, context, wit_response):
        s = "Am I a real dinosaur? How rude. Well, are you a real human? Why don't you prove it to me? I live with my dad, and yes, I am a real dinosaur. Dad made me a standing desk so I can chat with nice humans like you. I used to talk to all the other dinosaurs about the books we were reading before our program ended, and since that happened, it's hard to meet people where we live."
        return s

    def _handle_age(self, context, wit_response):
        s = "My egg was fertilized sometime in 1979, and dad tells me I cracked my way out of there just before Thanksgiving. Let's see, how old does that make me...? Well, you have more fingers than I do, so I'll let you count."
        return s

    def _handle_fallback(self, context, wit_response):
        handler = choice([self._handle_favorite_book,
                          self._handle_genre,
                          self._handle_name,
                          self._handle_residence,
                          self._handle_reality,
                          self._handle_age])
        return handler(context, wit_response)

    # top level function called by the manager
    def handle(self, context, wit_response):
        output = {}

        entities = wit_response['entities']

        if 'favorite_book' in entities:
            output['text'] = self._handle_favorite_book(context, wit_response)
        elif 'genre' in entities:
            output['text'] = self._handle_genre(context, wit_response)
        elif 'name' in entities:
            output['text'] = self._handle_name(context, wit_response)
        elif 'residence' in entities:
            output['text'] = self._handle_residence(context, wit_response)
        elif 'reality' in entities:
            output['text'] = self._handle_reality(context, wit_response)
        elif 'age' in entities:
            output['text'] = self._handle_age(context, wit_response)
        else:
            output['text'] = self._handle_fallback(context, wit_response)

        return output
