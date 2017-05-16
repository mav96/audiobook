import os

import libtorrent as lt
from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.http import Http404
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin, FormView
from django.core.files.storage import FileSystemStorage
from formtools.wizard.views import SessionWizardView

from audiobooks.models import AudioFile, AudioBook
from audiobooks.forms import TorrentFileForm, AudioBookForm


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
            torrent_info['path'] = os.path.abspath(torrent_file)
            return torrent_info
    except Exception as err:
        return None


class HomePageView(TemplateView):
    @method_decorator(login_required)
    def get(self, request, **kwargs):
        books = AudioBook.objects.filter(user=request.user)
        return render(request, 'index1.html',
                      {'books': books,
                       'host_url': "%s://%s/listen" % ('https' if request.is_secure() else 'http', request.get_host())})


class Listen(TemplateView):
    @method_decorator(login_required)
    def get(self, request, **kwargs):
        book_id = kwargs.get('book_id', None)
        url_list = ["%s://%s/mp3/%s" % ('https' if request.is_secure() else 'http', request.get_host(), url['id']) for
                    url in AudioFile.objects.filter(book_id=book_id).values('id')]
        return render(request, 'listen.html', {'url_list': url_list})


class Mp3(TemplateView):
    @method_decorator(login_required)
    def get(self, request, **kwargs):
        mp3_id = kwargs.get('mp3_id', None)
        file_name = AudioFile.objects.filter(id=mp3_id).values_list('file_name').get()[0]
        try:
            mp3file = open(file_name, "rb")
        except ValueError:
            raise Http404()
        response = HttpResponse(FileWrapper(mp3file), content_type='application/mp3')
        response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(file_name)
        return response


@login_required()
def list_file(request):
    # Handle file upload
    if request.method == 'POST':
        form = TorrentFileForm(request.POST, request.FILES)
        if form.is_valid():
            content_of_file = request.FILES['torrentfile'].read()
        #     newdoc = TorrentFile(docfile=request.FILES['torrentfile'])
        #     newdoc.save()

            filepath = settings.TORRENTS_DIR + "/123"
            with open(filepath, 'wb') as dest:
                dest.write(content_of_file)

        # Redirect to the document list_file after POST
        return HttpResponseRedirect(reverse('uploads'))
    else:
        form = TorrentFileForm()  # A empty, unbound form

    # Load documents for the list_file page

    # Render list_file page with the documents and the form
    return render(
        request,
        'upload.html',
        {'form': form}
    )


class TorrentFileUploadView(LoginRequiredMixin, SessionWizardView):
    form_list = [TorrentFileForm, AudioBookForm]
    title = "Upload torrent"
    template_name = 'book_add.html'
    file_storage = FileSystemStorage(
        location=os.path.join(settings.TORRENTS_DIR, 'tmp')
    )

    def get_form(self, step=None, data=None, files=None):
        form = super(TorrentFileUploadView, self).get_form(step, data, files)

        # determine the step if not given
        if step is None:
            step = self.steps.current

        if step == '1':
            tmp_file =self.storage.get_step_files('0').get('0-torrentfile').file.name
            info_torrent = check_mp3(tmp_file)
            form.initial = {
                'title': info_torrent['name']
            }
            form.instance.user = self.request.user
        return form

    def done(self, form_list, form_dict, **kwargs):
        form_dict['0'].upload_file()
        form_dict['1'].save()
        return HttpResponseRedirect(reverse('index'))
