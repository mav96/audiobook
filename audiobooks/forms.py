import os
import time
import uuid
import tempfile
import logging

# import libtorrent as lt
from django.forms import Form, FileField, ModelForm
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from audiobooks.models import AudioBook


logger = logging.getLogger(__name__)


def validate_file(value):
    import pdb; pdb.set_trace()

    return


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
    torrent_path = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)


class TorrentFileForm(Form):
    torrentfile = FileField(
        label='Select a torrent file',
        validators=[validate_file]
    )


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
