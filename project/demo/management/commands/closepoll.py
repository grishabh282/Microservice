import pika
from django.conf import settings
from django.core.management.base import BaseCommand
from pika.exceptions import ConnectionClosed
import json



class Command(BaseCommand):
    help = 'Sync Order to MarketPlace'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        
        super().__init__(stdout=None, stderr=None, no_color=False)
        self.RMQC = dict(settings.CMS_RABBITMQ_SETTINGS)
        self.RMQQ = dict(settings.RMQ_QUEUE["ORDER_SYNC_QUEUE"])
        credentials = pika.PlainCredentials(self.RMQC["USER"], self.RMQC["PASSWORD"])
        
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.RMQC["HOST"], self.RMQC["PORT"], self.RMQC.get("VHOST", "/"),
                                        credentials))                              
        channel = connection.channel()

    def handle(self, *args, **options):
        try:
            def callback(ch, method, properties, body):
                msg = body
                try:
                    msg = json.loads(body.decode("utf-8"))
                    print("msg==>", msg)
                    processOrder(msg)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as ee:
                    print("ERROR: syncOrder.py->callback function", ee, msg)
                    order_id = 0
                    if type(msg) is dict:
                        order_id = msg.get("id")
                    errorLog(order_id, 'order', 'sync_order_info_in_consumer', str(ee), msg)
                    raise ee

            credentials = pika.PlainCredentials(self.RMQC["USER"], self.RMQC["PASSWORD"])
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.RMQC["HOST"], self.RMQC["PORT"], self.RMQC.get("VHOST", "/"),
                                          credentials))
            channel = connection.channel()

            channel.exchange_declare(exchange=self.RMQQ["exchange_name"], exchange_type='fanout', durable=True)
            channel.queue_declare(queue=self.RMQQ["queue_name"], durable=True)
            channel.queue_bind(queue=self.RMQQ["queue_name"], exchange=self.RMQQ["exchange_name"],
                               routing_key=self.RMQQ["key_name"])

            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(self.RMQQ["queue_name"], callback, auto_ack=False)

            print(' [*] Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()

        except ConnectionClosed as e:
            print(e)

        except Exception as e:
            print(e)
