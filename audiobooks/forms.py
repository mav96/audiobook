import os
import time
import uuid
import tempfile
import logging

import libtorrent as lt
from django.forms import Form, FileField, ModelForm
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django import forms

from audiobooks.models import AudioBook


logger = logging.getLogger(__name__)


def check_torrent_file(f):
    e = lt.bdecode(f.read())
    try:
        t_info = lt.torrent_info(e)
    except Exception as err:
        raise forms.ValidationError("Something went wrong")
    files = [os.path.splitext(f.path)[1].upper()[1:] for f in t_info.files()]

    if "MP3" not in files:
        raise forms.ValidationError("Form doesn't have mp3 files")


def validate_file(value):
    if not hasattr(value, 'file'):
        raise forms.ValidationError("Doesn't have file")
    check_torrent_file(value.file)


def validate_magnet(value):
    magnet_uri = value
    ses = lt.session()
    params = {
        'save_path': settings.TORRENTS_DIR,
        'storage_mode': lt.storage_mode_t(2),
        'paused': False,
        'auto_managed': True,
        'duplicate_is_error': True}
    link = magnet_uri
    handle = lt.add_magnet_uri(ses, link, params)

    logger.debug('downloading metadata...')
    while not handle.has_metadata():
        time.sleep(1)

    torinfo = handle.get_torrent_info()
    torrent_file = lt.create_torrent(torinfo)
    with tempfile.TemporaryFile() as f:
        f.write(lt.bencode(torrent_file.generate()))
        check_torrent_file(f)


class TorrentFileForm(Form):
    torrentfile = FileField(
        label='Select a torrent file',
        validators=[validate_file]
    )

    def upload_file(self):
        # TODO write upload file
        pass


class AudioBookForm(ModelForm):
    class Meta:
        model = AudioBook
        fields = ('title', 'genre', 'language')
        labels = {
            "title": _('Book title'),
            "genre": _('Genre of Book'),
            "language": _('Language of book'),
        }
        # fields = ['title', 'authors']
