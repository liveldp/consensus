
import os

RABBIT_HOST = os.environ.get('RABBIT_HOST', 'localhost')
RABBIT_PORT = int(os.environ.get('RABBIT_PORT', 5672))
RABBIT_VH = os.environ.get('RABBIT_VH', '/')
RABBIT_USER = os.environ.get('RABBIT_USER', '***')
RABBIT_PASS = os.environ.get('RABBIT_PASS', '***')
RABBIT_EXCHANGE = os.environ.get('RABBIT_EXCHANGE', 'farolapp')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 2))
SPARQL_HOST = os.environ.get('SPARQL_HOST', 'localhost')
SPARQL_PORT = os.environ.get('SPARQL_PORT', 8890)
API_PORT = int(os.environ.get('API_PORT', 5001))


