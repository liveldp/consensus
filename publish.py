import json

import pika
import config

exchange = config.AMQP_EXCHANGE


def publish(data):
	connection_params = pika.ConnectionParameters(
	    host=config.AMQP_HOST, port=config.AMQP_PORT,
	    credentials=pika.credentials.PlainCredentials(config.AMQP_USER, config.AMQP_PASS)
	)
	connection = pika.BlockingConnection(connection_params)

	ch = connection.channel()

    	ch.basic_publish(exchange=exchange, routing_key='annotations.consensus', body=json.dumps(data))
    	print '{} -> |consensus|'.format(data)

	connection.close()
