#!/usr/bin/env python
"""
    sigas.rabbit_controller.turnstile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Virtual Rabbit Turnstile Client for testing.

    :copyright: (c) 2016 by Cooperativa de Trabajo BITSON Ltda.
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.group>.
    :license: AGPL, see LICENSE for more details.

    Usage:
        turnstile.py N [CONTROLLER] [--loglevel=LOGLEVEL] [--events-file=EVENTS] [--keep-alive] [--performance=PERFORMANCE]
        turnstile.py (-h | --help | -v | --version)
    
    Arguments:
        N               how many virtual turnstiles that you wanna run
        CONTROLLER      optional controller ip address or ip:port, 
                        default set to '127.0.0.1:4830'
        LOGLEVEL        CRITICAL    50
                        ERROR 	    40
                        WARNING     30
                        INFO        20 - default
                        DEBUG 	    10
                        NOTSET      0
        EVENTS          A CSV file containing Accesses & Exits

    Options:
        -v, --version   Prints software version
        -h, --help      This message help and exit
"""
# Standard lib imports
import csv
import pprint
import queue
# Third-party imports
from docopt import docopt
# BITSON imports
from virtual_turnstile import SERVER_PORT, TurnstileThread
from virtual_turnstile.logger import logger, ch


class MaxValueError(ValueError):
    pass


class MinValueError(ValueError):
    pass


if __name__ == '__main__':
    args = docopt(__doc__, version='0.0.1')
    debug = False

    if args['--loglevel']:
        ch.setLevel(level=args['--loglevel'])
        if args['--loglevel'] == 'DEBUG':
            debug = True

    keep_alive = True if args['--keep-alive'] else False

    # Validates argument N
    quantity = int(args['N'])
    if quantity > 255:
        raise MaxValueError('Virtual turnstiles should less than 255')
    if quantity < 1:
        raise MinValueError('Virtual turnstiles should be at least 1')

    # Parse argument CONTROLLER to controller_ip and controller_port
    controller_port = SERVER_PORT
    if args['CONTROLLER']:
        if ':' in args['CONTROLLER']:
            controller_ip, controller_port = args['CONTROLLER'].split(':')
            controller_port = int(controller_port)
        else:
            controller_ip = args['CONTROLLER']
    else:
        controller_ip = '127.0.0.1'

    performance = args['--performance'] or 'NORMAL'
    if performance == 'NORMAL':
        performance = '0'
    elif performance == 'FLEXIBLE':
        performance = '2'
        print('\033[33m❗ FLEXIBLE Mode detected\033[0m')
    elif performance == 'LIBERADO':
        performance = '6'
        print('\033[31m❗ LIBERADO Mode detected\033[0m')
    elif performance == 'OFF':
        performance = '1'
        print('\033[37m❗ FLEXIBLE Mode detected\033[0m')
    else:
        raise ValueError('\033[31mPerformances should be "NORMAL", "FLEXIBLE", "LIBERADO" or "OFF"\033[0m')

    logger.info(f'RABBIT CONTROLLER @ {controller_ip}:{controller_port}')

    q = queue.Queue()
    filename = args['--events-file']
    if filename:
        logger.info(f'Processing file \033[33m{filename}\033[0m')
        with open(filename, mode='r') as csv_file:
            reader = csv.reader(csv_file, delimiter=";")
            for row in reader:
                logger.debug(row)
                if row[8] == '1':
                    q.put(dict(command='21', id_tag=row[5], next_command='100'))
                elif row[8] == '0':
                    q.put(dict(command='21', id_tag=row[5], next_command='103'))
                elif row[8] == '-1':
                    q.put(dict(command='16', id_tag=row[5], next_command=''))
        logger.info(f'Loaded {q.qsize()} in events queue')
    else:
        logger.info(f'Working with demo info...')
        events = [
            dict(command='21', id_tag='82AFE7BD', next_command='100'),
            dict(command='21', id_tag='42495242', next_command='100'),
            dict(command='21', id_tag='0211AE92', next_command='103'),
            dict(command='21', id_tag='03907D28', next_command='100'),
            dict(command='21', id_tag='03C6518E', next_command='100'),
            dict(command='21', id_tag='31DA4928', next_command='100'),
            dict(command='21', id_tag='15A1070B', next_command='100'),
            dict(command='21', id_tag='8C835813', next_command='100'),
            dict(command='21', id_tag='8D935B38', next_command='100'),
            dict(command='21', id_tag='A507EC36', next_command='100'),
            dict(command='21', id_tag='756D24C9', next_command='100'),
            dict(command='21', id_tag='D50F23C9', next_command='100'),
            dict(command='21', id_tag='355323C9', next_command='100'),
            dict(command='21', id_tag='ADBC1234', next_command='100'),
            dict(command='8', id_tag='', next_command=''),
            dict(command='8', id_tag='', next_command=''),
            dict(command='8', id_tag='', next_command=''),
            dict(command='8', id_tag='', next_command=''),
            dict(command='8', id_tag='', next_command=''),
            dict(command='8', id_tag='', next_command=''),
        ]
        n = 1
        logger.info(f'Loading {len(events) * n} events')
        for i in range(n):
            for event in events:
                q.put(event)

    stop = False
    while not stop:
        if keep_alive:
            logger.info('Keep Alive mode detected --- Use Ctrl+C to kill ')
        print('\033[37m✔ Make sure you have Rabbit Controller running\033[0m')
        print('\033[37m✔ Make sure you have Monitor running\033[0m')
        print('\033[37m✔ Make sure you have an Open Event\033[0m')
        print('\033[37m✔ Make sure you have Imported a file\033[0m')
        answer = input('\033[32mDo you want to start? [Y/n] \033[0m')
        if answer in ['n', 'N', 'no', 'NO']:
            exit(1)
        if answer in ['', 'y', 'Y', 'yes', 'YES']:
            stop = True

    # Creating Turnstile Threads
    threads = []
    for i in range(quantity):
        turnstile_thread = TurnstileThread(
            # serial_number=f'00:00:00:00:00:{i+1:02X}',
            serial_number=f'00:00:00:00:00:{i+1:02}',
            ip=f'127.1.1.{i + 1}',
            controller_ip=controller_ip,
            controller_port=controller_port,
            events=q,
            performance=performance,
            )
        turnstile_thread.turnstile.logger = logger
        turnstile_thread.daemon = True
        turnstile_thread.start()
        threads.append(turnstile_thread)

    # Just for keeping alive the main thread
    while not q.empty():
        try:
            if keep_alive:
                q.put(dict(command='22'))
        except KeyboardInterrupt:
            logger.info('---- Ctrl-C Detected ----')
            exit(0)

    q.join()

    LECTURAS = dict(
        CONCEDIDO=0,
        YA_UTILIZADA=0,
        DADA_BAJA=0,
        INVALIDA=0,
        OTRO_TICKET=0,
        CUOTA_VENCIDA=0,
        SECTOR_INCORRECTO=0,
        PASO_PENDIENTE=0,
        TOTAL=0
    )
    PASADAS = dict(
        NORMAL=0,
        NORMAL_SIN_TARJETA=0,
        LIBERADA=0,
        LIBERADA_SIN_TARJETA=0,
        FLEXIBLE=0,
        FLEXIBLE_SIN_TARJETA=0,
        OFFLINE=0,
        OFFLINE_SIN_TARJETA=0,
        TOTAL=0
    )

    for turnstile_thread in threads:
        PASADAS['NORMAL'] += len(turnstile_thread.turnstile.report['PASADAS']['NORMAL']['CON_TARJETA'])
        PASADAS['NORMAL_SIN_TARJETA'] += len(turnstile_thread.turnstile.report['PASADAS']['NORMAL']['SIN_TARJETA'])
        PASADAS['LIBERADA'] += len(turnstile_thread.turnstile.report['PASADAS']['LIBERADA']['CON_TARJETA'])
        PASADAS['LIBERADA_SIN_TARJETA'] += len(turnstile_thread.turnstile.report['PASADAS']['LIBERADA']['SIN_TARJETA'])
        PASADAS['FLEXIBLE'] += len(turnstile_thread.turnstile.report['PASADAS']['FLEXIBLE']['CON_TARJETA'])
        PASADAS['FLEXIBLE_SIN_TARJETA'] += len(turnstile_thread.turnstile.report['PASADAS']['FLEXIBLE']['SIN_TARJETA'])
        PASADAS['OFFLINE'] += len(turnstile_thread.turnstile.report['PASADAS']['OFFLINE']['CON_TARJETA'])
        PASADAS['OFFLINE_SIN_TARJETA'] += len(turnstile_thread.turnstile.report['PASADAS']['OFFLINE']['SIN_TARJETA'])

        LECTURAS['CONCEDIDO'] += len(turnstile_thread.turnstile.report['LECTURAS']['CONCEDIDO'])
        LECTURAS['YA_UTILIZADA'] += len(turnstile_thread.turnstile.report['LECTURAS']['YA_UTILIZADA'])
        LECTURAS['DADA_BAJA'] += len(turnstile_thread.turnstile.report['LECTURAS']['DADA_BAJA'])
        LECTURAS['INVALIDA'] += len(turnstile_thread.turnstile.report['LECTURAS']['INVALIDA'])
        LECTURAS['OTRO_TICKET'] += len(turnstile_thread.turnstile.report['LECTURAS']['OTRO_TICKET'])
        LECTURAS['CUOTA_VENCIDA'] += len(turnstile_thread.turnstile.report['LECTURAS']['CUOTA_VENCIDA'])
        LECTURAS['SECTOR_INCORRECTO'] += len(turnstile_thread.turnstile.report['LECTURAS']['SECTOR_INCORRECTO'])
        LECTURAS['PASO_PENDIENTE'] += len(turnstile_thread.turnstile.report['LECTURAS']['PASO_PENDIENTE'])

        if debug:
            pprint.pprint(turnstile_thread.turnstile.report)

    PASADAS['TOTAL'] = sum(PASADAS.values())
    LECTURAS['TOTAL'] = sum(LECTURAS.values())
    pprint.pprint(PASADAS)
    pprint.pprint(LECTURAS)
    logger.info('Thanks for using me!')
