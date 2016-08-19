SECRET_KEY = 'wbyz6wEH7kQJFi'

DEBUG = True
RUN_PORT = 5000

URL_PREFIX = '/visor'

SERVERS = [
    {
        'alias': 'Mambo',
        'host': 'localhost',
        'port': 4730,
    },
    {
        'alias': 'Jumbo',
        'host': 'localhost',
        'port': 4731,
    },
    {
        'alias': 'Trumbo',
        'host': 'localhost',
        'port': 4732,
    },
]

CONNECT_TIMEOUT = 0.3
REQUEST_TIMEOUT = 0.5

# overriding settings on stage/prod
try:
    from gear_visor_settings import *
except ImportError:
    pass
