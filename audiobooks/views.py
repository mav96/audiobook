import os

from django.shortcuts import render
from django.http import Http404
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from wsgiref.util import FileWrapper

from audiobooks.models import AudioFile
from audiobooks.models import AudioBook
from audiobooks.forms import DocumentForm

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class HomePageView(TemplateView):
    @method_decorator(login_required)
    def get(self, request, **kwargs):
        books = AudioBook.objects.filter(userid=request.user.id)
        return render(request, 'index1.html',
                      {'books': books,
                       'host_url': "%s://%s/listen" % ('https' if request.is_secure() else 'http', request.get_host())})


class SearchForm(TemplateView):
    @method_decorator(login_required)
    def get(self, request, **kwargs):
        return render(request, 'search_form.html')


class Search(TemplateView):
    @method_decorator(login_required)
    def get(self, request, **kwargs):
        if 'q' in request.GET and request.GET['q']:
            q = request.GET['q']
            books = AudioBook.objects.filter(title__icontains=q)
            return render(request, 'search_results.html',
                          {'books': books, 'query': q})
        else:
            return HttpResponse('Please submit a search term.')


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

torrents_dir = './torrents'


@login_required()
def list_file(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            content_of_file = request.FILES['torrentfile'].read()
        #     newdoc = TorrentFile(docfile=request.FILES['torrentfile'])
        #     newdoc.save()

            filepath = torrents_dir + "/123"
            with open(filepath, 'wb') as dest:
                dest.write(content_of_file)

        # Redirect to the document list_file after POST
        return HttpResponseRedirect(reverse('uploads'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list_file page

    # Render list_file page with the documents and the form
    return render(
        request,
        'upload.html',
        {'form': form}
    )
