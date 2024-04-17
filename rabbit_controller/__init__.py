# -*- coding: utf-8 -*-
"""
    controller
    ~~~~~~~~~~

    This is the main module for turnstile's AC2001 Controller Board.

    :copyright: (c) 2016 by Cooperativa de Trabajo BITSON Ltda.
    :author: Leandro E. Colombo Viña.
    :license: GPL v3.0, see LICENSE for more details.

"""
# Standard lib imports
import logging
import logging.handlers
import os
import sys
import time
# Third Party imports
from rainbow_logging_handler import RainbowLoggingHandler
# BITSON imports
# from .constants import *
# from .putdlib import *
# from .server import *
from config import BASEDIR


__all__ = ["constants", "putdlib", "server"]

pidfile = "".join([BASEDIR, '/controller.pid'])

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_format = "".join(["[%(asctime)s] %(name)25s - %(levelname)7s: ",
                      "%(threadName)10s -%(funcName)15s() - %(message)s"])

formatter = logging.Formatter(fmt=log_format)
# Format UTC Time
formatter.converter = time.gmtime

# File Handler Logger
LOGDIR = os.path.join(BASEDIR, 'log')
if not os.path.isdir(LOGDIR):
    os.mkdir(LOGDIR)

LOGFILE = os.path.join(
    # BASEDIR,
    # '/log/',
    LOGDIR,
    #    os.path.basename(__file__).rstrip('.py'),
    'controller.log',
    )
fh = logging.handlers.RotatingFileHandler(filename=LOGFILE,
                                          maxBytes=10e6,
                                          backupCount=10)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Console Handler
# if sys.stdin.isatty():
ch = RainbowLoggingHandler(sys.stderr)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
