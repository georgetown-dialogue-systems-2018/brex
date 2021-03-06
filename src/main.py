import logging

# https://github.com/urllib3/urllib3/issues/1176
# sigh...
try:
    import gevent.monkey
    gevent.monkey.patch_all()
    from requests.packages.urllib3.util.ssl_ import create_urllib3_context
    create_urllib3_context()
except ImportError:
    pass

from brex.drivers.terminal_driver import TerminalDriver
from brex.drivers.flask_driver import FlaskDriver
from brex.wit_manager import WitManager
import brex.config as cfg

def download_deps():
    import nltk; nltk.download('punkt')

def main():
    download_deps()
    if not cfg.gr_api_key or not cfg.gr_api_secret or not cfg.wit_access_token:
        raise Exception("Goodreads and/or Wit secrets not found. Did you add them to brex/config.py?")

    logging.basicConfig(level=(logging.DEBUG if cfg.debug else logging.INFO))

    mode = cfg.mode
    manager = 'wit'

    if manager == 'wit':
        dm_class = WitManager

    # Drivers take a reference to a Manager constructor. The Driver handles user I/O and any other
    # UI work necessary, and it uses an instance of the Manager to decide how to respond.
    if mode == 'terminal':
        TerminalDriver(dm_class).run()
    elif mode == 'flask':
        FlaskDriver(dm_class).run()

if __name__ == '__main__':
    main()
