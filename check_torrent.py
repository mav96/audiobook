import libtorrent as lt
import os


def check_mp3(torrent_file):
    torrent_info = dict()
    try:
        with open(torrent_file, 'rb') as f:
            e = lt.bdecode(f.read())
            torinfo = lt.torrent_info(e)
            torrent_info['name'] = torinfo.name()
            torrent_info['hash'] = torinfo.info_hash()
            torrent_info['num_files'] = torinfo.num_files()
            torrent_info['mp3_size'] = 0
            torrent_info['size'] = 0
            for filename in torinfo.files():
                torrent_info['size'] += filename.size
                if os.path.splitext(filename.path)[1].upper()[1:] == "MP3":
                    torrent_info['mp3_size'] += filename.size
            return torrent_info
    except Exception as err:
        return None

d = check_mp3("/home/super/PycharmProjects/DATA/torrents/1.torrent1")
if d is None:
    print("Bad")
else:
    print(d)