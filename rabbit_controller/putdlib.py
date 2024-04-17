# -*- coding: utf-8 -*-
"""
    putdlib
    ~~~~~~~

    This is the module for turnstile's messages packages protocol in AC2001
    Controller Board.

    :copyright: (c) 2016 by Cooperativa de Trabajo BITSON Ltda.
    :author: Leandro E. Colombo Viña.
    :license: GPL v3.0, see LICENSE for more details.

"""
# Standard lib imports
from binascii import hexlify
import logging
from datetime import datetime


PKG_START_STR = '<'
PKG_SEPARATOR_STR = ';'
PKG_END_STR = '>'
PKG_KV_SEPARATOR_STR = '='
PKG_CMD_STR = 'COMANDO'
PKG_CHK_STR = 'PUTDCHK'
PKG_DATETIME_STR_FORMAT = "%Y%m%d%H%M%S%f"

logger = logging.getLogger(__name__)


class PUTD():
    """Manages data between AC2001 board and Controller server for UDP packages.

    :param from_text: A string of the form ``<KEY1=VALUE1;KEY2=VALUE2;...;>``.
    :param command: An integer, command value.
    :param options: A dictionary with the options to sent.
    """

    def __init__(self, from_text=None, command=None, options=None):
        self.logger = logging.getLogger(__name__)
        if from_text:
            self.logger.info("---- >>>>>>> Creating PUTD from %s", from_text)
            if isinstance(from_text, str):
                self.options = dict(
                    i.split('=') for i in from_text.strip('<>').split(';')[:-1]
                    )
            elif isinstance(from_text, bytes):
                self.options = dict()
                for option in from_text.strip(b'<>').split(b';')[:-1]:
                    key, value = option.split(b'=')
                    key = key.decode('utf-8')
                    try:
                        value = value.decode('utf-8')
                    except UnicodeError:
                        self.logger.warning("utf-8 error: %s", from_text)
                        value = hexlify(value).decode('utf-8').upper()
                    finally:
                        self.options[key] = value
                self.options.pop(PKG_CHK_STR)
                self.options[PKG_CHK_STR] = self._calc_checksum(self._parse_for_checksum())
            else:
                raise NotImplementedError
            self.cmd = int(self.options.get(PKG_CMD_STR))
            self._chk = int(self.options.pop(PKG_CHK_STR))
        else:
            # if DEBUG: self.logger.debug(
            #   "Creating PUTD with cmd: %s and opt: %s", command, options)
            self.options = options if options else dict()
            self.cmd = command
            self._chk = None

    @property
    def cmd(self):
        return self.__cmd

    @cmd.setter
    def cmd(self, cmd):
        self.__cmd = cmd
        self.options[PKG_CMD_STR] = str(cmd)

    def __repr__(self):
        return str(self.options)

    def __str__(self):
        return self.parse()

    def _set_timestamp(self):
        now = datetime.utcnow().strftime(PKG_DATETIME_STR_FORMAT)[:-3]
        # if DEBUG: self.logger.debug("Updating time: {}".format(now))
        self.options['FECHAHORA'] = now

    def parse(self):
        """Returns options ready for UDP package

        :rtype: A string in the format <KEY1=VALUE1; KEY2=VALUE2; ... ;>
        """
        data = self._parse_for_checksum()
        self._chk = self._calc_checksum(data)
        # Agregamos el checksum al paquete
        data = "".join([
            data,
            PKG_SEPARATOR_STR,     # ";"
            PKG_CHK_STR,           # "PUTDCHK"
            PKG_KV_SEPARATOR_STR,  # "="
            str(self._chk),        # "checksum value"
            PKG_SEPARATOR_STR])    # ";"
        # Agregamos los símbolos de menor (<) y mayor (>)
        return "".join([data, PKG_END_STR])

    def _parse_for_checksum(self):
        # Armamos la lista de opciones según Key=Value
        option_list = [
            PKG_KV_SEPARATOR_STR.join([k, v]) for k, v in self.options.items()
            ]
        # Unimos las opciones con el ";"
        data = PKG_SEPARATOR_STR.join(option_list)
        # Devolvemos el string listo para calcular el checksum
        return "".join([PKG_START_STR, data])

    @staticmethod
    def _calc_checksum(data, encoding='utf-8'):
        """Calculates string Checksum.

        :param data: A string.
        :rtype: An integer representing :param:`data` checksum value
        """
        return sum(bytearray(data, encoding), -1) % 1000

    def is_valid(self):
        response = self._chk == self._calc_checksum(self._parse_for_checksum())
        return response

    def send(self, encoding='utf-8', appmgr=False):
        if not appmgr:
            self._set_timestamp()
        self.options = dict([k, str(v)] for k, v in self.options.items())
        self.logger.info("---- >>>>>>> sending command %s", self.cmd)
        return self.parse().encode(encoding)
