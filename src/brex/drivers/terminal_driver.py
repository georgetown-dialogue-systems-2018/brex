from brex.drivers.driver import Driver

class TerminalDriver(Driver):
    def __init__(self, dm_class):
        self._dm = dm_class()

    def run(self):
        exit = False
        while not exit:
            user_input = input('=> ').strip()
            response = self._dm.respond(user_input)
            print("response", response)
            exit = response['exit']
            print(response['text'])

