import libtorrent as lt
import time
import os
import shutil
import pika
import json
import sys
import logging
import getopt


LOG_FORMAT = ('%(levelname) -10s %(asctime)s: %(message)s')
LOGGER = logging.getLogger(__name__)



class DownloadManager():

    def __init__(self, amqp_url):
        self.ses = lt.session()
        self.ses.listen_on(6881, 6891)
        self.handles = {}
        self.connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='book_task', durable=True)
        #self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='book_task')

        self.status_connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
        self.status_channel = self.status_connection.channel()
        self.status_channel.queue_declare(queue='book_status')
        self.status_channel.basic_consume(self.check_status, queue='book_status')



        LOGGER.info('Service started')



    @staticmethod
    def print_torrent_info(torinfo):
        LOGGER.info(torinfo.name())
        LOGGER.info(torinfo.info_hash())
        LOGGER.info(torinfo.num_files())
        # for x in torinfo.files():
        #     print(x.path, " size is ", x.size)

    @staticmethod
    def get_torrent_info(torrent_file):
        if os.path.exists(torrent_file):
            with open(torrent_file, 'rb') as f:
                e = lt.bdecode(f.read())
                return True, lt.torrent_info(e)
        return False, None


    def get_handle(self, torinfo, files_dir):
        params = {'save_path': "{0}/{1}".format(files_dir, torinfo.info_hash()),
                      'storage_mode': lt.storage_mode_t.storage_mode_sparse, 'ti': torinfo}
        return self.ses.add_torrent(params)


    def callback(self, ch, method, properties, body):
        new_queue = {}
        data = json.loads(body)
        torrent_file = data['torrent_file']
        files_dir = data['data_dir']
        book_uid = properties.correlation_id
        if book_uid not in self.handles.keys():
            b, t = self.get_torrent_info(torrent_file)
            if b:
                h = self.get_handle(t, files_dir)
                self.print_torrent_info(t)
                new_queue['handle'] = h
                new_queue['ch'] = ch
                new_queue['body'] = json.loads(body)
                new_queue['metod'] = method
                        
                self.handles[book_uid] = new_queue
            else:
                LOGGER.info('Error: file %s not found' % torrent_file)
                ch.basic_ack(delivery_tag = method.delivery_tag)
        else:
            if 'remove' in data:
                remove_torrent(book_uid)



    def check_status(self, ch, method, props, body):
        book_uid = props.correlation_id
        data = json.loads(body)
        status = {}
        state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']
        status['book_id'] = book_uid
        if book_uid in self.handles.keys():
            s = self.handles[book_uid]['handle'].status()
            status['pogress'] = s.progress *100
            status['state'] = s.state
            status['active'] = 1
        else:
            torrent_file = data['torrent_file']
            files_dir = data['data_dir']
            b, t = self.get_torrent_info(torrent_file)
            if b:
                if os.path.exists("{0}/{1}".format(files_dir, t.info_hash())):
                    h = self.get_handle(t, files_dir)
                    s = h.status()
                    while 'checking' in str(s.state):
                        s = h.status()
                        time.sleep(1)
                    status['pogress'] = s.progress *100
                    status['state'] = state_str[s.state]
                    status['active'] = 0
                    self.ses.remove_torrent(h)

        ch.basic_publish(exchange='', routing_key=props.reply_to, 
                        properties=pika.BasicProperties(correlation_id = book_uid), body=json.dumps(status))
        ch.basic_ack(delivery_tag = method.delivery_tag)


    def process_events(self):
        self.connection.process_data_events()
        self.status_connection.process_data_events()
        del_list = []
        for (b, h) in self.handles.items():
            s = h['handle'].status()
            if s.is_seeding:
                self.ses.remove_torrent(h['handle'])
                print("the book with uid %s downloaded" % b)
                del_list.append(b)
            else:
                print('the book with uid %s: %.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % (b,
                s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers, s.state))

        for b in del_list:
            #print(" [x] Book %s Done" % self.handles[b]['body']['book_id'])
            LOGGER.info(" [x] Book %s Done" % self.handles[b]['body']['book_id'])
            self.handles[b]['ch'].basic_ack(delivery_tag = self.handles[b]['metod'].delivery_tag)
            del self.handles[b]

    def remove_torrent(self, book_uid):
        if book_uid in self.handles:
            self.ses.remove_torrent(self.handles[book_uid]['handle'])
            self.handles[b]['ch'].basic_ack(delivery_tag = self.handles[b]['metod'].delivery_tag)
            del self.handles[book_uid]
            LOGGER.info('Book with id %s removed form download', book_uid)



    def close(self):
        if self.connection.is_open:
            self.connection.close()
        if self.status_connection.is_open:
            self.status_connection.close()
        LOGGER.info('Stopped')    



def main(argv):
    url = 'amqp://guest:guest@localhost:5672/'
    #url = 'amqp://myprojectuser:password@mqserver:5672/'    

    try:
        opts, args = getopt.getopt(argv,"hu:",["url="])
    except getopt.GetoptError:
        print('%s -u <url>' % sys.argv[0])
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('\n%s -u <url>' % sys.argv[0])
            print("\nExample: %s -u amqp://myprojectuser:password@mqserver:5672/" % sys.argv[0])
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg

    
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    dm = DownloadManager(url)
    try:	
        while True:
            dm.process_events()
            time.sleep(2)
    except KeyboardInterrupt:
        dm.close()
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
