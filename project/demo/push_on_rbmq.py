import pika

from django.conf import settings

_connection = None
_channel = None


def _create_connection():
    credentials = pika.credentials.PlainCredentials(username=settings.CMS_RABBITMQ_SETTINGS['USER'],
                                                    password=settings.CMS_RABBITMQ_SETTINGS['PASSWORD'])
    return pika.BlockingConnection(pika.ConnectionParameters(host=settings.CMS_RABBITMQ_SETTINGS['HOST'],
                                                             credentials=credentials))


def _create_channel():
    global _connection
    channel = _connection.channel()
    channel.exchange_declare(exchange=settings.SALES_FORCE_ORDER_EXCHANGE,
                             exchange_type='fanout', durable=True)
    channel.queue_declare(queue="queue_name_dev", durable=True) 
    channel.queue_bind(queue="queue_name_dev", exchange=settings.SALES_FORCE_ORDER_EXCHANGE,
                               routing_key="order_sync_queue_consumer")                        
    return channel


def main_channel():
    global _connection
    global _channel
    if _connection is None or not _connection.is_open:
        _connection = _create_connection()
        _channel = _create_channel()
    elif _channel is None or not _channel.is_open:
        _channel = _create_channel()
    return _channel


def publish_to_exchange(body):

    response = main_channel().basic_publish(exchange=settings.SALES_FORCE_ORDER_EXCHANGE,
                                            routing_key='',
                                            body=body,
                                            properties=pika.BasicProperties(
                                                delivery_mode=2,  # make message persistent
                                                content_type='application/json'
                                            ))
   
    return response


def close():
    global _connection
    _connection.close()
