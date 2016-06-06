import json

import pika
import config

exchange = config.RABBIT_EXCHANGE

connection_params = pika.ConnectionParameters(
    host=config.RABBIT_HOST, port=config.RABBIT_PORT,
    credentials=pika.credentials.PlainCredentials(config.RABBIT_USER, config.RABBIT_PASS)
)
connection = pika.BlockingConnection(connection_params)

ch = connection.channel()


def publish(data):
    ch.basic_publish(exchange=exchange, routing_key='annotations.consensus', body=json.dumps(data))
    print '{} -> |consensus|'.format(data)
