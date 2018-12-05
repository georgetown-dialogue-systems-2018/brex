from brex.drivers.driver import Driver

class TerminalDriver(Driver):
    def __init__(self, dm_class):
        self._dm = dm_class()

    def run(self):
        should_exit = False
        while not should_exit:
            user_input = input('=> ').strip()
            response = self._dm.respond(user_input)
            should_exit = response['exit'] if 'exit' in response else should_exit
            print(response['text'])
