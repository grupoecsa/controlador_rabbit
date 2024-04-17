SERVER_PORT = 4830
TURNSTILE_PORT = 4831

PERFORMANCE = {
    100: 'Normal',
    101: 'Fuera de Serv.',
    102: 'En Pánico',
    103: 'En Upgrade',
    104: 'En Transfer',
    105: 'Reiniciando',
    106: 'Liberado',
    107: 'Pánico-Liber-NoPerfo',
    108: 'Pánico-Liberado',
    109: 'Pánico-NoPerfora',
    110: 'Liberado-NoPerfora',
    111: 'No Perfora',
    }

COMMANDS = {
    # """Turnstile Notifications"""
    1: 'ntfPasadaOffline',       # {Deprecated}
    2: 'ntfVerificarPosicion',   # {X}
    3: 'ntfSectorErroneo',       # {X}
    4: 'ntfEventoErroneo',       # {X}
    5: 'ntfErrorDeHardware',     # {X}
    6: 'ntfInicioSesion',        # {X}
    7: 'ntfFinSesion',           # {X}
    8: 'ntfPasadaSinTarjeta',    # {X}
    9: 'ntfCaidaMolinete',       # {X}
    10: 'ntfSubidaMolinete',     # {X}
    11: 'ntfEntradaEnPanico',    # {X}
    12: 'ntfSalidaDePanico',     # {X}
    13: 'ntfErrorCRCProtix',     # {X}
    14: 'ntfOle',                # {X}
    15: 'ntfTarjetasSolapadas',  # {X}
    16: 'ntfSalida',             # {X}
    17: 'ntfMolineteRemovido',   # {X}
    18: 'ntfPasadaEnPanico',     # {Deprecated}
    19: 'ntfTarjetaYaUsada',     # {Uso interno del server}
    20: 'ntfTarjetaAnulada',     # {Uso interno del server}
    21: 'ntfTarjetaVencida',     # {Uso interno del server}
    22: 'ntfErrorEstadoProtix',  # {Uso interno del server}
    23: 'ntfTarjetaNoExiste',    # {Uso interno del server}
    29: 'ntfClubIncorrecto',     # {X}
    30: 'ntfYaTieneTicket',      # {Uso interno del server}
    32: 'ntfSeasonErronea',      # {Uso interno del server}
    32: 'ntfPasadaLiberada',     # {X}
    33: 'ntfEntrarEnLiberado',   # {X}
    34: 'ntfSalirDeLiberado',    # {X}
    35: 'ntfCredencialVencida',  # {Uso interno del server}
    100: 'ntfPasada',            # {X}
    101: 'ntfDesbloquear',       # Esta notificacion desbloquea tarjetas
    103: 'ntfTimeoutPasada',
    # """Turnstile Questions""",
    21: 'qstVerificarTarjeta',  # {X}
    22: 'qstServerVivo',        # {X}
    23: 'qstNuevaVersion',      # {-}
    24: 'qstPedirFragmento',    # {-}
    25: 'qstFileInfo',          # {-}
    26: 'qstComando',           # {X}
    27: 'qstConfiguracion',     # {X}
    28: 'qstSectores',          # {X}
    # """Controller responses"""
    61: 'rspTarjetaOk',          # {X}
    62: 'rspTarjetaYaUsada',     # {X}
    63: 'rspTarjetaVencida',     # {X}
    64: 'rspTarjetaAnulada',     # {X}
    65: 'rspTarjetaNoExiste',    # {X}
    66: 'rspServerVivo',         # {X}
    67: 'rspNuevaVersion',       # {-}
    68: 'rspFragmentoErroneo',   # {-}
    69: 'rspArchivoIncorrecto',  # {-}
    70: 'rspFragmento',          # {-}
    71: 'rspFileInfo',           # {-}
    71: 'rspEstadoErroneo',      # {X}
    73: 'rspComando',            # {X}
    74: 'rspNoHayComandos',      # {X}
    75: 'rspSectorCompleto',     # {No usado}
    76: 'rspYaTieneTicket',      # {X}
    77: 'rspSeasonErronea',      # {X}
    78: 'rspGanoUnPremio',       # Usado para credencial no ingresada
    79: 'rspEsAbonoAdicional',   # {X}
    80: 'rspCredencialVencida',  # {X}
    83: 'rspSectorIncorrecto',
    84: 'rspEventoIncorrecto',
    101: 'rspTarjetaEnEspera',   # {X}
    102: 'rspConfiguracion',     # Dice que lo que viene es la configuración.
    # """Others"""
}

DESCRIEVANOM = [
    ''
    'Pasada Off-Line',
    'Error de Lectura',
    'Sector Erróneo',
    'Evento Erróneo',
    'Error de Hardware',
    'Inicio de Sesión',
    'Fin de Sesión',
    'Pasada sin Tarjeta',
    'Caída de Molinete',
    'Subida de Molinete',
    'Entrada modo Pánico',
    'Salida modo Pánico',
    'Error CRC de Protix',
    'Tarjeta Retirada',
    'Tarjetas Solapadas',
    'Egreso',
    '',
    'Pasada en Pánico',
    'Tarjeta ya Utilizada',
    'En Lista Negra',
    'Cuota Vencida',
    'Error de Estado',
    'Tarjeta No Emitida',
    '',
    '',
    '',
    '',
    '',
    'Club Incorrecto',
    'Ya Tiene Ticket',
    'Season Errónea',
    'Pasada Liberada',
    'Entr. modo Liberado',
    'Salida modo Liberado',
    'Credencial Vencida',
]
