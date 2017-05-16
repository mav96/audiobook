import pika
import json
import sys


class BookStatus():

    def __init__(self, amqp_url):
#        credentials = pika.PlainCredentials('myprojectuser', 'password')
#        self.connection = pika.BlockingConnection(pika.ConnectionParameters('mqserver',5672,'/',credentials))
        self.connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, data):
        book_uid = data['book_id']
        self.response = None
        self.corr_id = book_uid
        self.channel.basic_publish(exchange='',
                                   routing_key='book_status',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=json.dumps(data))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


def main():
    data = {}
    data['book_id'] = sys.argv[1] or '999'
    data['torrent_file'] = sys.argv[2]  or '/home/mav/WORK/audiobook/torrents/1.torrent'
    data['data_dir'] = sys.argv[3] or '/home/mav/WORK/audiobook/data'

    rpc = BookStatus('amqp://myprojectuser:password@mqserver:5672/')

    print(" [x] Requesting Book %s" % data['book_id'])
    response = rpc.call(data)
    print(" [.] Got %s" % response)

if __name__ == '__main__':
    main()


