import logging

from brex.handlers.handler import Handler
from brex.template_renderer import TemplateRenderer
from brex.summarize import summarize
import brex.config as cfg
from brex.config import summarization_sentence_count as initial_sentence_count
import brex.goodreads as gr
import names

DINO_DICT = {
    'a': 'Atrociraptor',
    'b': 'Brachyceratops',
    'c': 'Chasmosaurus',
    'd': 'Deinodon',
    'e': 'Edmontosaurus',
    'f': 'Formosibittacus',
    'g': 'Gorgosaurus',
    'h': 'Hadrosaurus',
    'i': 'Invicatrx',
    'j': 'Judiceratops',
    'k': 'Kosmoceratops',
    'l': 'Lophorhothon',
    'm': 'Mojoceratops',
    'n': 'Nasutoceratops',
    'o': 'Ojoraptorsaurus',
    'p': 'Polyonax',
    'q': 'Quaesitosaurus',
    'r': 'Rajasaurus',
    's': 'Saurolophus',
    't': 'Tachiraptor',
    'u': 'Utahraptor',
    'v': 'Velociraptor',
    'w': 'Weewarrasaurus',
    'x': 'Xenoceratops',
    'y': 'Yandusaurus',
    'z': 'Zanabazar'
}

requestable_entities = ['title', 'author', 'summary', 'rating']

class Request(Handler):
    def __init__(self):
        self._renderer = TemplateRenderer('request')
        self._last_discussed_book = None
        self._reviews = None

    def _fetch_summary(self, context, wit_response, book):
        # make sure we have reviews
        self._reviews = self._reviews or gr.reviews(book.gid)
        if len(self._reviews) == 0:
            return {'failure': 'no_reviews'}

        # begin with the whole review
        summary = self._reviews[0]
        logging.debug("Found a review with {} chars...".format(len(summary)))

        # attempt to summarize if it's too long
        sentence_count = initial_sentence_count
        prev_summary = ""
        while len(summary) > cfg.summarization_max_chars:
            sentence_count -= 1
            prev_summary = summary
            summary = summarize(self._reviews[0], sentence_count = sentence_count)
            logging.debug("After summarization: {} chars".format(len(summary)))

        # summarization might have returned nothing with a low sentence count
        # back off to the last one that had text
        if not summary:
            summary = prev_summary or self._reviews[0]

        # discard the review we've successfully sent to the user
        self._reviews = self._reviews[1:]
        return {'summary': summary}

    def _fetch_entity(self, context, wit_response, entity):
        book = context['current_book']
        if self._last_discussed_book != book:
            self._last_discussed_book = book
            self._reviews = None

        if not book:
            return {'failure': 'no_current_book'}
        elif entity == 'title':
            return {'title': book.title}
        elif entity == 'author':
            return {'author': book.authors}
        elif entity == 'summary':
            return self._fetch_summary(context, wit_response, book)
        elif entity == 'rating':
            return {'rating': book.average_rating}
        else:
            raise Exception('Tried to request an unsupported entity: {}'.format(entity))

    def _generate_friend_name(self):
        first_name = names.get_first_name()
        first_letter = first_name[0].lower()
        last_name = DINO_DICT[first_letter]
        return first_name + " " + last_name

    def _generate_text(self, context, wit_response, system_intent):
        if 'failure' in system_intent:
            reason = system_intent['failure']
            if reason == 'no_current_book':
                return self._renderer.render('no_current_book')
            if reason == 'no_reviews':
                return self._renderer.render('no_reviews')
            else:
                raise Exception('Tried to generate text for unknown failure "{}"'.format(reason))
        elif 'title' in system_intent:
            title = system_intent['title']
            return self._renderer.render('title', {'title': title})
        elif 'author' in system_intent:
            authors = system_intent['author']
            author = authors[0]
            return self._renderer.render('author', {'author': author})
        elif 'summary' in system_intent:
            summary = system_intent['summary']
            friend = self._generate_friend_name()
            return self._renderer.render('summary', {'summary': summary,
                                                     'friend': friend})
        elif 'rating' in system_intent:
            rating = system_intent['rating']
            return self._renderer.render('rating', {'rating': rating})
        else:
            raise Exception('Tried to generate text for some unknown entity. System intent: {}'.format(system_intent))

    def handle(self, context, wit_response):
        entities = wit_response['entities']
        system_intent = {}
        for entity, value in entities.items():
            if entity in requestable_entities:
                result = self._fetch_entity(context, wit_response, entity)
                logging.debug("Fetched entity: " + str(result))
                if 'failure' in result:
                    system_intent = result
                    break
                else:
                    # i.e., merge the `result` dict into `system_intent`
                    system_intent.update(result)

        if len(system_intent.keys()) == 0:
            logging.error("Encountered a request without an intent. Falling back to giving a summary.")
            system_intent.update(self._fetch_entity(context, wit_response, "summary"))

        logging.debug("System intent: {}".format(system_intent))

        return self._generate_text(context, wit_response, system_intent)
