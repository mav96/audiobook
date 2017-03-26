# -*- coding: utf-8 -*-

from django import forms


class DocumentForm(forms.Form):
    torrentfile = forms.FileField(
        label='Select a torrent file'
    )