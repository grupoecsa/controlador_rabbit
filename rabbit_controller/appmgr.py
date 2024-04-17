#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

"""This is the main module for AC2001 Application Manager.
"""
# Standard lib imports
import logging
import logging.handlers
import os
import socket
import socketserver
import sys
import time
from rainbow_logging_handler import RainbowLoggingHandler

import putdlib

__author__ = "Leandro E. Colombo Viña <colomboleandro@bitson.com.ar>"
__copyright__ = "Copyright (C) 2014 Leandro E. Colombo Viña"
__license__ = "GPL 3.0"

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_format = "".join(["[%(asctime)s] %(name)s - %(levelname)8s: ",
                      "%(threadName)15s <%(thread)15s> - %(message)s"])

formatter = logging.Formatter(fmt=log_format)
# Format UTC Time
formatter.converter = time.gmtime

# File Handler Logger
LOGFILE = "".join([
    BASE_DIR,
    '/log/',
    os.path.basename(__file__).rstrip('.py'),
    '.log'
    ])
fh = logging.handlers.RotatingFileHandler(filename=LOGFILE,
                                          maxBytes=10e6, backupCount=10)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Console Handler
ch = RainbowLoggingHandler(sys.stderr)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

putdlib.PKG_CMD_STR = 'CMD'
RABBIT_PORT = 1024
APPMGR_PORT = 4840

offer = putdlib.PUTD(command='APPOFFER')
offer.options["DESCRIPTION"] = 'Application Manager ver 1.0.4.0 en VM-WINXP'
offer.options["HOSTNAME"] = 'VM-WINXP'
offer.options["VERSION"] = '1.0.4.0'
offer.options["PRODUCTCODE"] = 'ECSA-U-E-MM'
offer.options["SERIALNUMBER"] = 'S03001'

server_info = putdlib.PUTD(command='SERVERINFO')
server_info.options["CONNECTIONTYPE"] = "2"
server_info.options["BAUDRATE"] = "9600"
server_info.options["DATABITS"] = "8"
server_info.options["STOPBITS"] = "1"
server_info.options["PARITY"] = "0"
server_info.options["NODE485"] = "0"
server_info.options["IPADDRESS"] = "192.168.1.253"
server_info.options["IPMASK"] = "255.255.255.0"
server_info.options["IPGATEWAY"] = "0.0.0.0"
server_info.options["IPDNS"] = "0.0.0.0"
server_info.options["PARAM1"] = "SERVERIP|192.168.1.55"
server_info.options["PARAM2"] = "SERVERPORT|4830"
server_info.options["PARAM3"] = "TIMEOUT|5"
server_info.options["PARAM4"] = "TIMERETRY|10"
server_info.options["PARAM5"] = "TURNSTILE|1"
server_info.options["PARAM6"] = "GATE|11"
server_info.options["PRODUCTCODE"] = "ECSA-U-E-MM"
server_info.options["SERIALNUMBER"] = "S03001"


class AppManagerUDPHandler(socketserver.BaseRequestHandler):
    """Receives a package from AC2001 Turnstile and passes initial configs.
    """
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('AppMgrUDPHandler: __init__')
        socketserver.BaseRequestHandler.__init__(self, request,
                                                 client_address, server)
        return

    def setup(self):
        self.logger.debug('AppMgrUDPHandler: setup')
        return socketserver.BaseRequestHandler.setup(self)

    def handle(self):
        data = self.request[0].strip()
        cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        cs.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if b'CMD=APPDISCOVER' in data:
            cs.sendto(offer.send(), ('<broadcast>', RABBIT_PORT))
            cs.sendto(server_info.send(), ('<broadcast>', RABBIT_PORT))
            self.logger.debug("Configuration SENT!")

    def finish(self):
        self.logger.debug('AppMgrUDPHandler: finish')
        return socketserver.BaseRequestHandler.finish(self)


class ApplicationManager(socketserver.ThreadingMixIn, socketserver.UDPServer):
    def __init__(self, server_address, handler_class=AppManagerUDPHandler):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('AppManager: __init__')
        socketserver.UDPServer.__init__(self, server_address, handler_class)
        return

    def server_activate(self):
        self.logger.debug('AppManager: server_activate')
        socketserver.UDPServer.server_activate(self)
        return

    def serve_forever(self):
        self.logger.debug('AppManager: waiting for request')
        self.logger.info('Handling requests, press <Ctrl-C> to quit')
        while True:
            self.handle_request()
        return

    def handle_request(self):
        # if DEBUG: self.logger.debug('AppManager: handle_request')
        return socketserver.UDPServer.handle_request(self)

    def verify_request(self, request, client_address):
        # if DEBUG: self.logger.debug('AppManager: verify_request(%s, %s)',
        #                             request, client_address)
        return socketserver.UDPServer.verify_request(self, request,
                                                     client_address)

    def process_request(self, request, client_address):
        # if DEBUG: self.logger.debug('AppManager: process_request(%s, %s)',
        #                              request, client_address)
        return socketserver.UDPServer.process_request(self, request,
                                                      client_address)

    def server_close(self):
        # if DEBUG: self.logger.debug('AppManager: server_close')
        return socketserver.UDPServer.server_close(self)

    def finish_request(self, request, client_address):
        # if DEBUG: self.logger.debug('AppManager: finish_request(%s, %s)',
        #                              request, client_address)
        return socketserver.UDPServer.finish_request(self, request,
                                                     client_address)

    def close_request(self, request_address):
        # if DEBUG: self.logger.debug('AppManager: close_request(%s)',
        #                              request_address)
        return socketserver.UDPServer.close_request(self, request_address)


if __name__ == "__main__":
    logger.info("Starting Controller application, hit <Ctrl-C> to quit")
    logger.debug("Logging is working")
    HOST, PORT = '', APPMGR_PORT
    logger.debug("Binding IP: {}, PORT: {}".format(HOST, PORT))
    server = ApplicationManager((HOST, PORT))
    logger.info("Server listening")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.debug("You hit <Ctrl-C>, exiting...")
        logger.info("Closing server")
        server.server_close()
        logger.info("Server closed")
