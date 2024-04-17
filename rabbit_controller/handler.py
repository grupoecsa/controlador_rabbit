"""
    sigas.rabbit_controller.handler
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Description

    :copyright: (c) 2016 by Cooperativa de Trabajo BITSON Ltda..
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""

# Standard lib imports
import os
import logging
import socketserver
import threading
from rabbit_controller.baccess import *
from rabbit_controller.putdlib import PUTD
from getmac import get_mac_address

class DBTest:
    pass

TURNSTILES = {}
PASADAS_TURNSTILES = {}

class RabbitControllerUDPHandler(socketserver.BaseRequestHandler):
    """Receives a package from AC2001 Turnstile and makes a valid response.
    """
    use_baccess = os.getenv('BACCESS') == 'True'

    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger(__name__)
        self.event = None
        self.socket = request[1]
        self.putd = PUTD(from_text=request[0])
        self.turnstile = None
        self.card = None
        self.cards = []
        self.id_tag = ""
        self.db = None
        self.orientation = 1
        socketserver.BaseRequestHandler.__init__(self, request, client_address,
                                                 server)


    def handle(self):
        """Creates a new thread to process request """
        t = threading.Thread(target=self.process_request)
        t.daemon = True
        t.start()

    def process_request(self):
        """Parses message and call the corresponding method
        """
        if self.use_baccess:
            ts_position = int(self.putd.options.get("MOLINETE"))
            ts_gate = int(self.putd.options.get("PUERTA"))
            ts_type = self.putd.options.get('MODELOMOLINETE')
            ingresos = int(self.putd.options.get("INGRESOS"))
            salidas = int(self.putd.options.get("SALIDAS"))
            performance = 100 + int(self.putd.options.get("PERFORMANCE"))
            mac = get_mac_address(ip=self.client_address[0])
            ip = self.client_address[0],

            partials = PASADAS_TURNSTILES.get(mac)

            if partials:
                old_ingresos = partials.get('ingresos')
                old_salidas = partials.get('salidas')
                if ingresos > old_ingresos and salidas == old_salidas:
                    self.orientation = 1
                elif salidas > old_salidas and ingresos == old_ingresos:
                    self.orientation = -1
                else:
                    self.orientation = 1

            PASADAS_TURNSTILES[mac] = {'ingresos': ingresos, 'salidas': salidas}

            self.id_tag = self.putd.options.get("TARJETA") or self.putd.options.get("DATA")
            if self.id_tag and '@' in self.id_tag:
                self.id_tag = self.id_tag.replace("@", "").replace("M", "").replace('F', '')

            if self.putd.cmd == 22:
                if TURNSTILES.get(mac):
                    card = TURNSTILES.get(mac).get('card')
                    if card:
                        response = baccess_send_command(command=103,
                                                        ip=ip,
                                                        mac=mac,
                                                        card=card,
                                                        turnstile=self,
                                                        performance=performance)
                        TURNSTILES.pop(mac)
            if self.putd.cmd == 11:
                print('Cambio a flexible')
                p = PUTD(command=66)
                self.socket.sendto(p.send(), self.client_address)
                return

            if self.putd.cmd == 33:
                print('Cambio a liberado')
                p = PUTD(command=66)
                self.socket.sendto(p.send(), self.client_address)
                return

            if self.putd.cmd == 26:
                if TURNSTILES.get(mac):
                    command = TURNSTILES.get(mac).get('command')
                    if not command:
                        p = PUTD(command=66)
                        self.socket.sendto(p.send(), self.client_address)
                        return
                    if isinstance(command, int):
                        command = [command]
                    options = dict(
                        CODIGOCOMANDO=command[0],
                    )
                    print(f' Enviando {command[0]} de {command}')
                    TURNSTILES.pop(mac)
                    command.pop(0)
                    if len(command) > 0:
                        TURNSTILES[mac] = {'command': command}
                    p = PUTD(command=73, options=options)
                    self.socket.sendto(p.send(), self.client_address)
                return

            if TURNSTILES.get(mac):
                command = TURNSTILES.get(mac).get('command')
                if command:
                    options = dict(COMANDOPENDIENTE=1)
                    p = PUTD(command=66, options=options)
                    self.socket.sendto(p.send(), self.client_address)
                    return

            response = baccess_send_command(command=self.putd.cmd,
                                            ip=ip,
                                            mac=mac,
                                            card=self.id_tag,
                                            turnstile=self,
                                            orientation=self.orientation,
                                            performance=performance)
            print(response)
            p = PUTD(command=66)
            if self.putd.cmd == 27:
                p = PUTD(command=102, options=response)
                self.socket.sendto(p.send(), self.client_address)
            elif self.putd.cmd == 28:
                p = PUTD(command=66, options=response)
                self.socket.sendto(p.send(), self.client_address)
            elif self.putd.cmd in [10, 34]:
                p = PUTD(command=66, options=response)
                self.socket.sendto(p.send(), self.client_address)
            elif self.putd.cmd == 100:
                if TURNSTILES.get(mac):
                    TURNSTILES.pop(mac)
                p = PUTD(command=66, options=response)
            elif self.putd.cmd == 21:
                if response:
                    if response.get('idmensaje') in [61, 62, 64, 65, 83, 80]:
                        if response.get('idmensaje') == 61:
                            TURNSTILES[mac] = {'card': self.id_tag}
                        p = PUTD(command=response.get('idmensaje'))
                    else:
                        p = PUTD(command=66)
            else:
                if process_keep_alive(response) == 66:
                    p = PUTD(command=66)
                else:
                    TURNSTILES[mac] = {'command': process_keep_alive(response)}
                    print(TURNSTILES[mac])
                    options = dict(
                        COMANDOPENDIENTE=1,
                    )
                    p = PUTD(command=66, options=options)
            self.socket.sendto(p.send(), self.client_address)
            return

    def keep_alive(self):
        """Response to the turnstile question cmd=22 with a cmd=66.

            Checks if Turnstile has Pending command and add it Pending command count to the respons

        :return: PUTD string to the turnstile
        """
        options = dict(EVENTO=0)
        p = PUTD(command=66, options=options)  # rspServerVivo

        command_count = self.turnstile.get_pending_commands_count()
        if command_count:
            message = f'{self.turnstile} -> Pending Command Count: {command_count}'
            self.logger.info(message)
            p.options['COMANDOPENDIENTE'] = command_count
        else:
            message = f'{self.turnstile} -> Keep Alive'
            self.logger.debug(message)

        return p.send()

