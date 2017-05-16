import pika
import sys
import json

def main():
    _url = 'amqp://myprojectuser:password@mqserver:5672/'
#    credentials = pika.PlainCredentials('myprojectuser', 'password')
#    connection = pika.BlockingConnection(pika.ConnectionParameters('mqserver',5672,'/',credentials))
    connection = pika.BlockingConnection(pika.URLParameters(_url))

    channel = connection.channel()
    channel.queue_declare(queue='book_task', durable=True)


    data = {}
    data['book_id'] = sys.argv[1] or "999"
    data['torrent_file'] = sys.argv[2]  or "/torrents/file.torrent"
    data['data_dir'] = sys.argv[3] or "/data"


    book_id = data['book_id'] 

    message = json.dumps(data) 



    channel.basic_publish(exchange='',
                          routing_key='book_task',
                          properties=pika.BasicProperties(correlation_id = book_id, 
                                                          delivery_mode = 2,
                                                         ),
                          body=message)


    print(" [x] Sent new file")
    connection.close()

if __name__ == '__main__':
        main()

