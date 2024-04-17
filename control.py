#!/usr/bin/env python
"""
    Rabbit Turnstile Controller Server Script
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Script server module for turnstile's AC2001 Controller Board.

    :copyright: (c) 2016 by Cooperativa de Trabajo BITSON Ltda.
    :author: Leandro E. Colombo Viña.
    :license: GPL v3.0, see LICENSE for more details.

    Usage:
        control.py [CONTROLLER] [--loglevel=LOGLEVEL]
        control.py (-h | --help | -v | --version)

    Arguments:
        CONTROLLER      optional controller ip address or ip:port,
                        default set to '*:4830'
        LOGLEVEL        CRITICAL    50
                        ERROR 	    40
                        WARNING     30
                        INFO        20 - default
                        DEBUG 	    10
                        NOTSET      0

    Options:
        -v, --version   Prints software version
        -h, --help      This message help and exit

"""

# Standard lib imports
# Third-party imports
from docopt import docopt
# BITSON imports
from rabbit_controller import ch
from rabbit_controller.server import RabbitController, __version__
from rabbit_controller.constants import SERVER_PORT


if __name__ == "__main__":
    args = docopt(__doc__, version=__version__)

    if args['--loglevel']:
        ch.setLevel(level=args['--loglevel'])

    # Parse argument CONTROLLER to controller_ip and controller_port
    controller_port = SERVER_PORT
    if args['CONTROLLER']:
        if ':' in args['CONTROLLER']:
            controller_ip, controller_port = args['CONTROLLER'].split(':')
            if controller_ip == '0':
                controller_ip = '0.0.0.0'
            controller_port = int(controller_port)
        else:
            controller_ip = args['CONTROLLER']
    else:
        controller_ip = '0.0.0.0'

    server = RabbitController(ip=controller_ip, port=int(controller_port))
    server.logger.info(f'RABBIT CONTROLLER @ {controller_ip}:{controller_port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.logger.debug("You hit <Ctrl-C>, exiting...")
        server.server_close()
        server.logger.info("Server closed")
