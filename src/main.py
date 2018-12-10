import logging

from brex.drivers.terminal_driver import TerminalDriver
from brex.drivers.flask_driver import FlaskDriver
from brex.wit_manager import WitManager
import brex.config as cfg

def main():
    if not cfg.gr_api_key or not cfg.gr_api_secret or not cfg.wit_access_token:
        raise Exception("Goodreads and/or Wit secrets not found. Did you add them to brex/config.py?")

    logging.basicConfig(level=(logging.DEBUG if cfg.debug else logging.INFO))

    mode = cfg.mode
    manager = 'wit'

    if manager == 'wit':
        dm_class = WitManager

    if mode == 'terminal':
        TerminalDriver(dm_class).run()
    elif mode == 'flask':
        FlaskDriver(dm_class).run()

if __name__ == '__main__':
    main()
