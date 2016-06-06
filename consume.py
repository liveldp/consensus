from threading import Thread

import pika


def __setup_channel(exchange, routing_key, queue, callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost', credentials=pika.credentials.PlainCredentials('farolapp', 'oeg2016')))

    channel = connection.channel()
    channel.exchange_declare(exchange=exchange,
                             type='topic', durable=True)

    channel.queue_declare(queue, durable=True)
    channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)
    # channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=queue)
    channel.start_consuming()


def start_channel(exchange, routing_key, queue, callback):
    def wrap_callback(channel, method, properties, body):
        try:
            callback(method, properties, body)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except (SyntaxError, TypeError, ValueError) as e:
            print e.message
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        except Exception, e:
            print e.message
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=True)

    th = Thread(target=__setup_channel, args=[exchange, routing_key, queue, wrap_callback])
    th.daemon = True
    th.start()
