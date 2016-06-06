
import os

AMQP_HOST = os.environ.get('AMQP_HOST', 'localhost')
AMQP_PORT = int(os.environ.get('AMQP_PORT', 5672))
AMQP_VH = os.environ.get('AMQP_VH', '/')
AMQP_USER = os.environ.get('AMQP_USER', '***')
AMQP_PASS = os.environ.get('AMQP_PASS', '***')
AMQP_EXCHANGE = os.environ.get('AMQP_EXCHANGE', 'farolapp')
DATA_HOST = os.environ.get('DATA_HOST', 'localhost')
DATA_PORT = int(os.environ.get('DATA_PORT', 6379))
DATA_DB = int(os.environ.get('DATA_DB', 2))
SPARQL_HOST = os.environ.get('SPARQL_HOST', 'localhost')
SPARQL_PORT = os.environ.get('SPARQL_PORT', 8890)
API_PORT = int(os.environ.get('API_PORT', 5001))


