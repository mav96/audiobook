# -*- coding: utf-8 -*-

from django.forms import Form, FileField, ModelForm
from django.utils.translation import ugettext_lazy as _


from audiobooks.models import AudioBook


class DocumentForm(Form):
    torrentfile = FileField(
        label='Select a torrent file'
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
