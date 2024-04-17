# -*- coding: utf-8 -*-
"""
    controller server
    ~~~~~~~~~~~~~~~~~

    This is the server module for turnstile's AC2001 Controller Board.

    :copyright: (c) 2016 by Cooperativa de Trabajo BITSON Ltda.
    :author: Leandro E. Colombo Viña.
    :license: GPL v3.0, see LICENSE for more details.

"""
# Standard lib imports
import logging
import os
import socketserver
# Third-party imports
from flask import Flask
# BITSON imports
from . import pidfile, logger
from .multiplatform import filelock
from .handler import RabbitControllerUDPHandler
from config import config


__version__ = '0.1.6'




class RabbitController(socketserver.ThreadingMixIn, socketserver.UDPServer):
    """Rabbit Turnstile Controller Main Server.

    :param ip: Rabbit Controller IP Address.
    :param port: Rabbit Contrller Server Port.
    :param timeout: Retry timeout to reconnection attempt into DB.
    :param handler_class: UDP Handler class for this use case.
    """
    socketserver.UDPServer.max_packet_size = 1024

    def __init__(self, ip, port, timeout=2,
                 handler_class=RabbitControllerUDPHandler):
        self.logger = logging.getLogger(__name__)
        self.ip = ip
        self.port = port
        self.timeout = timeout
        server_address = (ip, port)
        socketserver.UDPServer.__init__(self, server_address, handler_class)
        self.db = None
        return

    def serve_forever(self, poll_interval=0.5):
        with filelock(pidfile):
            # Writes pidfile with pid number inside
            with open(pidfile, 'w') as f:
                pid = os.getpid()
                f.write(str(pid))

            # Getting Flask APP configuration
            config_name = os.getenv('FLASK_CONFIG') or 'default'
            self.app = Flask(__name__)
            self.app.config.from_object(config[config_name])

            # Start Controller connecting to DB
            logger.info("Starting Rabbit Controller, hit <Ctrl-C> to quit")
            with self.app.app_context():
                self.logger.info('Handling requests, press <Ctrl-C> to quit')
                while True:
                    super().serve_forever()

    def server_close(self):
        if os.path.isfile(pidfile):
            with open(pidfile) as f:
                pid = f.readline().strip()
                logger.info(f'Killing controller with PID {pid}')
            os.remove(pidfile)
        else:
            logger.error('Controller is not running')
            exit(1)

        logger.info('Closing server')
        return socketserver.UDPServer.server_close(self)
