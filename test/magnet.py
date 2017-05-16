import libtorrent as lt
import time
import os
import shutil
import django

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

torrents_dir = '/home/mav/WORK/audiobook/torrents'

link = "magnet:?xt=urn:btih:460A191FB88E6B66A9E62B45BE1AE169B0876988&tr=http%3A%2F%2Fbt.t-ru.org%2Fann%3Fmagnet&dn=%D0%90%D0%BA%D1%83%D0%BD%D0%B8%D0%BD%20%D0%91%D0%BE%D1%80%D0%B8%D1%81%20-%20%D0%9C%D0%B5%D0%B6%D0%B4%D1%83%20%D0%95%D0%B2%D1%80%D0%BE%D0%BF%D0%BE%D0%B9%20%D0%B8%20%D0%90%D0%B7%D0%B8%D0%B5%D0%B9.%204%2C%20%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%20%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%BE%D0%B3%D0%BE%20%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B0.%20%D0%A1%D0%B5%D0%BC%D0%BD%D0%B0%D0%B4%D1%86%D0%B0%D1%82%D1%8B%D0%B9%20%D0%B2%D0%B5%D0%BA%20%5B%D0%90%D0%BB%D0%B5%D0%BA%D1%81%D0%B0%D0%BD%D0%B4%D1%80%20%D0%9A%D0%BB%D1%8E%D0%BA%D0%B2%D0%B8%D0%BD%2C%202016%2C%20~96%20kbps%2C%20MP3%5D"
magnet_to_torrent(link, 1, torrents_dir)
