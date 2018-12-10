import logging

from brex.handlers.handler import Handler
from brex.template_renderer import TemplateRenderer


requestable_entities = ['title', 'author', 'summary', 'rating']

class Request(Handler):
    def __init__(self):
        self._renderer = TemplateRenderer('request')

    def _fetch_entity(self, context, wit_response, entity):
        book = context['current_book']

        if not book:
            return {'failure': 'no_current_book'}
        elif entity == 'title':
            return {'title': book.title}
        elif entity == 'author':
            return {'author': book.authors}
        elif entity == 'summary':
            return {'summary': book.description}
        elif entity == 'rating':
            return {'rating': book.average_rating}
        else:
            raise Exception('Tried to request an unsupported entity: {}'.format(entity))

    def _generate_book_response(self, context, wit_response, system_intent):
        book = context['current_book']
        return self._renderer.render('book', {'book': book})

    def _generate_text(self, context, wit_response, system_intent):
        if 'failure' in system_intent:
            reason = system_intent['failure']
            if reason == 'no_current_book':
                return self._renderer.render('no_current_book')
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
            return self._renderer.render('summary', {'summary': summary})
        elif 'rating' in system_intent:
            rating = system_intent['rating']
            return self._renderer.render('rating', {'rating': rating})
        else:
            raise Exception('Tried to generate text for some unknown entity. System intent: {}'.format(system_intent))

    def handle(self, context, wit_response):
        output = {}

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

        output['text'] = self._generate_text(context, wit_response, system_intent)

        return output
