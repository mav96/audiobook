import libtorrent as lt
import time
import os
import shutil
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home_server.settings")
django.setup()
from audiobooks.models import AudioFile
from audiobooks.models import AudioBook

torrents_dir = './torrents'
files_dir = './cache'


def magnet_to_torrent(magnet_uri, book_uid, dst):
    ses = lt.session()
    params = {
        'save_path': dst,
        'storage_mode': lt.storage_mode_t(2),
        'paused': False,
        'auto_managed': True,
        'duplicate_is_error': True}
    link = magnet_uri
    handle = lt.add_magnet_uri(ses, link, params)

    print('downloading metadata...')
    while not handle.has_metadata():
        s = handle.status()
        time.sleep(1)

    torinfo = handle.get_torrent_info()
    torrent_file = lt.create_torrent(torinfo)
    torrent_path = os.path.join(dst, "{0}.torrent".format(book_uid))
    with open(torrent_path, "wb") as f:
        f.write(lt.bencode(torrent_file.generate()))
    print("Torrent saved to %s" % torrent_path)
    return torrent_path


class DownloadManager():
    def __init__(self):
        self.ses = lt.session()
        self.ses.listen_on(6881, 6891)
        self.handles = {}

    @staticmethod
    def print_torrent_info(torinfo):
        print(torinfo.name())
        print(torinfo.info_hash())
        print(torinfo.num_files())
        # for x in torinfo.files():
        #     print(x.path, " size is ", x.size)

    @staticmethod
    def get_torrent_info(torrent_file):
        with open(torrent_file, 'rb') as f:
            e = lt.bdecode(f.read())
            return lt.torrent_info(e)

    def add_torrent(self, book_uid):
        torrent_file = "{0}/{1}.torrent".format(torrents_dir, book_uid)
        if os.path.exists(torrent_file):
            torinfo = self.get_torrent_info(torrent_file)
            self.print_torrent_info(torinfo)
            params = {'save_path': "{0}/{1}".format(files_dir, torinfo.info_hash()),
                      'storage_mode': lt.storage_mode_t.storage_mode_sparse, 'ti': torinfo}
            h = self.ses.add_torrent(params)
            self.handles[book_uid] = h
            # DataBase
            AudioFile.objects.filter(book_id=book_uid).delete()
            for filename in torinfo.files():
                if os.path.splitext(filename.path)[1].upper()[1:] == "MP3":
                    AudioFile.objects.create(book_id=book_uid,
                                             file_name="{0}/{1}/{2}".format(files_dir, torinfo.info_hash(), filename.path))
            ##
        else:
            print('Error: file ', torrent_file, ' not found')
            # DataBase
            ab = AudioBook.objects.filter(id=book_uid)
            for object in ab:
                object.torrent_status = 'no'
                object.save()
            ##

    def check_torrents(self):
        del_list = []
        for (b, h) in self.handles.items():
            s = h.status()
            if s.is_seeding:
                self.ses.remove_torrent(h)
                print("the book with uid ", b, " downloaded")
                # DataBase
                ab = AudioBook.objects.filter(id=b)
                for object in ab:
                    object.torrent_status = 'ready'
                    object.save()
                ##
                del_list.append(b)
            else:
                print("the book with uid ", b, ': %.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % (
                s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers, s.state))
                # DataBase
                ab = AudioBook.objects.filter(id=b)
                for object in ab:
                    object.torrent_status = '%.2f%% complete %s' % (s.progress * 100, s.state)
                    object.save()
                ##
        for b in del_list:
            del self.handles[b]

    def remove_torrent(self, book_uid):
        if book_uid in self.handles:
            self.ses.remove_torrent(self.handles[book_uid])
            del self.handles[book_uid]
        # DataBase
        ab = AudioBook.objects.filter(id=book_uid)
        for object in ab:
            object.to_listen = False
            object.torrent_status = 'yes'
            object.save()
        AudioFile.objects.filter(book_id=book_uid).delete()
        ##


# link = "magnet:?xt=urn:btih:460A191FB88E6B66A9E62B45BE1AE169B0876988&tr=http%3A%2F%2Fbt.t-ru.org%2Fann%3Fmagnet&dn=%D0%90%D0%BA%D1%83%D0%BD%D0%B8%D0%BD%20%D0%91%D0%BE%D1%80%D0%B8%D1%81%20-%20%D0%9C%D0%B5%D0%B6%D0%B4%D1%83%20%D0%95%D0%B2%D1%80%D0%BE%D0%BF%D0%BE%D0%B9%20%D0%B8%20%D0%90%D0%B7%D0%B8%D0%B5%D0%B9.%204%2C%20%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%BE%D0%B3%D0%BE%20%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B0.%20%D0%A1%D0%B5%D0%BC%D0%BD%D0%B0%D0%B4%D1%86%D0%B0%D1%82%D1%8B%D0%B9%20%D0%B2%D0%B5%D0%BA%20%5B%D0%90%D0%BB%D0%B5%D0%BA%D1%81%D0%B0%D0%BD%D0%B4%D1%80%20%D0%9A%D0%BB%D1%8E%D0%BA%D0%B2%D0%B8%D0%BD%2C%202016%2C%20~96%20kbps%2C%20MP3%5D"
# magnet_to_torrent(link, 3, torrents_dir)

dm = DownloadManager()

# check torrents
print("Update torrent's files")
ab = AudioBook.objects.all()
for object in ab:
    torrent_file = "{0}/{1}.torrent".format(torrents_dir, object.id)
    if os.path.exists(torrent_file):
        torinfo = dm.get_torrent_info(torrent_file)
        object.torrent_hash = torinfo.info_hash()
        object.torrent_status = 'yes'
    else:
        object.torrent_hash = ''
        object.torrent_status = 'no'
    object.save()

# add to download
print('Add torrents to download:')
ab = AudioBook.objects.filter(to_listen=True)
for object in ab:
    if object.torrent_status == 'no':
        print('No torrent!!!')
    else:
        dm.add_torrent(object.id)

# remove files
print('Remove files in cache...')
ab = AudioBook.objects.filter(to_listen=False)
for object in ab:
    if os.path.exists("{0}/{1}".format(files_dir, object.torrent_hash)):
        shutil.rmtree("{0}/{1}".format(files_dir, object.torrent_hash))

while True:
    dm.check_torrents()
    time.sleep(5)
