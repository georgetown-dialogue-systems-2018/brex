import logging

from brex.drivers.terminal_driver import TerminalDriver
from brex.wit_manager import WitManager
import brex.config as cfg

def main():
    logging.basicConfig(level=(logging.DEBUG if cfg.debug else logging.INFO))

    mode = 'terminal'
    manager = 'wit'

    if manager == 'wit':
        dm_class = WitManager

    if mode == 'terminal':
        TerminalDriver(dm_class).run()

if __name__ == '__main__':
    main()
