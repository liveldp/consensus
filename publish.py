import json

import pika

exchange = 'farolapp'

connection_params = pika.ConnectionParameters(
    host='localhost', port=5672, credentials=pika.credentials.PlainCredentials('farolapp', 'oeg2016')
)
connection = pika.BlockingConnection(connection_params)

ch = connection.channel()


def publish(data):
    ch.basic_publish(exchange=exchange, routing_key='annotations.consensus', body=json.dumps(data))
    print '{} -> |consensus|'.format(data)
