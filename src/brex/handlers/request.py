from brex.handlers.handler import Handler

requestable_entities = ['title', 'author', 'review']
class Request(Handler):
    def __init__(self):
        pass

    def _fetch_entity(self, context, wit_response, entity):
        book = context['current_book']

        if not book:
            return {'failure': 'no_current_book'}
        elif entity == 'title':
            return {'title': book.title}
        elif entity == 'author':
            return {'author': book.authors}
        elif entity == 'summary':
            return {'description': book.description}
        else:
            raise Exception('Tried to request an unsupported entity: {}'.format(entity))

    def _generate_text(self, context, wit_response, system_intent):
        return str(system_intent)

    def handle(self, context, wit_response):
        output = {}

        entities = wit_response['entities']
        system_intent = {}
        for entity, value in entities.items():
            if entity in requestable_entities:
                result = self._fetch_entity(self, context, wit_response, entity)
                if 'failure' in result:
                    system_intent = result
                    break
                else:
                    # i.e., merge the `result` dict into `system_intent`
                    system_intent.update(result)

        output['text'] = self._generate_text(context, wit_response, system_intent)

        return output
