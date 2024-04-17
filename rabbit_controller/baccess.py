
import requests
import json
from configparser import ConfigParser
import datetime

ecsa_to_baccess_states = {100: 1,
                          102: 2,
                          106: 3,
                          108: 3,
                          101: 3,
                          110: 4,
                          111: 5,
                          }

ecsa_to_baccess_orientation = {0: 1,
                               1: 1,
                               -1: 2,
                               3: 3}

ecsa_to_baccess_orientation_2 = {
    0: 1,
    1: 2,
    'timeout': 3
}

bacces_to_ecsa_responses = {'1': True,
                            '0': False,
                            }

command_to_state = {
    900: 1,
    901: 2,
    902: 3,
    903: 3,
    904: 4,
    905: 5
}

baccess_command = {
    #send_turnstile_info
    '711': 'ecsa_setinfo',
    #register_stand_alone_turn = '900'
    '900': 'ecsa_checkacceso',
    #register_stand_alone_timeout = '901'
    '901': 'ecsa_checkacceso',
    #register_turn_anomaly = '8'
    '8': 'ecsa_checkacceso',
    '16': 'ecsa_checkacceso',
    '32': 'ecsa_checkacceso',

    #handshake = '10'
    '10': 'ecsa_keepalive',
    #validate_access = '21'
    '21': 'ecsa_checkacceso',
    #keep_alive = '22'
    '22': 'ecsa_keepalive',
    #pull_turnstile_access_list = '32'
    '332': 'ecsa_getlistas',
    #register_turn = '100'
    '100': 'ecsa_checkacceso',
    #register_timeout = '103'
    '103': 'ecsa_checkacceso',
    '710': 'ecsa_settotallistas',
}

#
example = {
    "codigo": "2111116",
    "macaddress": 35,
    "modo": 1,
    "tipo": 1,
}

parser = ConfigParser()
parser.read('baccess.ini')
config = parser._sections

token = config.get('baccess').get('token', '9639e2cedbc77f1f471ead57e89bedderfdgfdsgds345se231')
url = config.get('baccess').get('ip_server', '83.48.71.25')
port = config.get('baccess').get('port_server', '9445')

def get_header():
    header = {"content-type": "application/json",
              "Authorization": token}
    return header

def send_msg(command, msg=None):
    if not msg:
        msg = json.dumps(example)
    rsp = {}
    try:
        cmd = baccess_command.get(command)
        full_url = 'http://%s:%s/%s' % (url, port, cmd)
        print(full_url)
        header = get_header()
        msg = json.dumps(msg)
        rsp = requests.post(full_url, headers=header, data=msg, timeout=0.8)
        if cmd == 'ecsa_checkacceso':
            print('validate')
        if rsp.status_code == 200:
            print('Success!')
            return rsp.json()
        elif rsp.status_code == 404:
            print('Not Found.')
            return {}
        elif rsp.status_code == 500:
            print('Error')
            return {}

    except Exception as e:
        print(e)
    return {}

def baccess_send_command(command=None, turnstile=None, card=None, orientation=0, **kwargs):
    print(command)
    ip = kwargs.get('ip')
    mac = kwargs.get('mac')
    state_mol = ecsa_to_baccess_states[kwargs.get('performance')]
    tipo = ecsa_to_baccess_orientation[orientation]

    if command in [27, 34]:
        return return_config(turnstile)
    if command == 28:
        return return_sector()
    if command == 100:
        print('Pasada')
        return ''
        message = f'Turn Detected in EMERGENCY MODE'
    if command == 16:
        tipo = ecsa_to_baccess_states[111]
        message = f'Turn Detected OUT in FLEXIBLE MODE'
    if command == 8:
        message = f'Turn Detected without a CARD'
        tipo = ecsa_to_baccess_states[110]
    if command == None:
        return [b'False', b'Error'], False
    if str(command) in ['101', '103']:
        tipo = 3
    msg = {"macaddress": mac,
           "codigo": card,
           "tipo": tipo,
           "modo": state_mol}

    if int(command) == 710:
        if kwargs.get('add_data'):
            msg['listas'] = kwargs.get('add_data')

    if int(command) == 711:
        if kwargs.get('add_data'):
            msg = kwargs.get('add_data')
            msg['macaddress'] = mac

    if int(command) > 899:
        msg['codigo_estado'] = command_to_state.get(command)
        if kwargs.get('date'):
            msg['fecha'] = kwargs.get('date')
        if kwargs.get('idProductoPase'):
            msg['idProductoPase'] = kwargs.get('idProductoPase')

    return send_msg(str(command), msg)



def notificate(turnstile, card, cmd, state):
    if not turnstile.baccess_api_id:
        get_id_from_baccess_api(turnstile)
    state_mol = ecsa_to_baccess_states[state]
    tipo = ecsa_to_baccess_orientation[cmd]
    msg = {"idLector": turnstile.board.mac,
           "codigo": card,
           "tipo": tipo,
           "modo": state_mol}
    rsp = send_msg('validate', msg)


def get_id_from_baccess_api(turnstile):
    msg = {'MAC_ADDRESS': turnstile.board.mac}
    rsp = send_msg('get_turnstile_id', msg)
    return rsp.get('idLector')

def process_keep_alive(response):
    msg = response.get('mensaje')
    has_resp = response.get('resp')

    if has_resp == 1:
        if msg == 'no':
            print('Estado Normal')
            command = {'values': {'performance': 100}}
            return [6, 11, 0]

        if msg == 'fl':
            print('Estado Flexible')
            command = {'values': {'performance': 102}}
            return [11, 5]

        if msg == 'li':
            print('Estado Liberado')
            return [10, 5]

        if msg == 'cl':
            print('Consulta Listas')

        if msg == 'lb':
            print('Pedir lista blanca')

        if msg == 'ln':
            print('Pedir lista negra')

        if msg == 'de':
            print('Eliminar listas')

        if msg == 're':
            print('Reset')
            return 2

        if msg == 'in':
            print('enviar info')
    return 66

def return_sector():
    options = dict(
        EVENTO=1,
        SECTORES="123/45/6789",
    )
    return options

def return_config(data):
    state = 100 + int(data.putd.options.get("PERFORMANCE"))
    gate = 10
    position = 10
    timeout = 20
    options = dict(
        PUERTA=gate,
        MOLINETE=position,
        EVENTOEMERGENCIA=999,
        ESTADIO="LC",
        NOPERFORAR="00",
        PERMITIRABONOS=1,
        PERMITIRSOCIOS=1,
        USARPULSADOR=1,
        USARLRC=1,
        USARCRCCAKS=1,
        USARCRCTAKS=1,
        USARCRCSUKS=1,
        USARCRCBAKS=1,
        USARCRCIAKS=1,
        CTRLEVENTO=1,
        CTRLVERPOSICION=1,
        CTRLCUOTA=1,
        CTRLNOEMITIDA=1,
        CONTROLABONOS=0,
        TIMEOUTPASADA=timeout,
        MODELO=1,
        MODELOMOLINETE=1,
        PERFORAR=1 if state in [107, 109, 110, 111] else 0,
        LIBERADO=1 if state in [106, 107, 108] else 0,
        PANICO=1 if state in [102, 107, 108, 109] else 0,
        PERMITIRDMJ=1,
        EVENTO=0,
    )
    return options  # rspConfiguracion


"""
from firmware.baccess import *
rsp = send_msg('validate')
"""


