import os

from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.http import Http404
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.http import HttpResponseRedirect
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


class HomePageView(TemplateView):
    @method_decorator(login_required)
    def get(self, request, **kwargs):
        books = AudioBook.objects.filter(userid=request.user.id)
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


class AudioBookCreateView(CreateView, FormMixin):
    template_name = 'book_add.html'
    model = AudioBook
    form_class = AudioBookForm

    # def form_valid(self, form):
    #     candidate = form.save(commit=False)
    #     candidate.user = UserProfile.objects.get(user=self.request.user)  # use your own profile here
    #     candidate.save()
    #     return HttpResponseRedirect(self.get_success_url())


class TorrentFileUploadView(SessionWizardView):
    form_list = [TorrentFileForm, AudioBookForm]
    title = "Upload torrent"
    # form_class = TorrentFileForm
    template_name = 'book_add.html'
    # file = ''os.path.join(settings.TORRENTS_DIR, 'tmp')
    file_storage = FileSystemStorage(location=os.path.join(settings.TORRENTS_DIR, 'tmp'))

    def process_step(self, form):
        step_data = self.get_form_step_data(form)
        if self.steps.current == '0':
            import pdb;pdb.set_trace()

        return step_data

    def process_step_files(self, form):
        return self.get_form_step_files(form)

    def done(self, form_list, **kwargs):

        # do_something_with_the_form_data(form_list)
        return HttpResponseRedirect('/')

    def get_form(self, step=None, data=None, files=None):
        form = super(TorrentFileUploadView, self).get_form(step, data, files)

        # determine the step if not given
        if step is None:
            step = self.steps.current

        if step == '1':
            form.user = self.request.user
        return form
    # def get_success_url(self):
    #     return reverse_lazy('book-add', kwargs={'file_name': self.file})
    #
    # def form_valid(self, form):
    #     self.file = form.upload_file()
    #     return super(TorrentFileUploadView, self).form_valid(form)
    # def get_context_data(self, **kwargs):
    #     context = super(TorrentFileUploadView, self).get_context_data(
    #         **kwargs)
    #     context['title'] = self.title
    #     return context
    # def form_invalid(self, form):

