from django.conf.urls import url
from audiobooks import views


urlpatterns = [
    url(r'^$', views.HomePageView.as_view(),  name='index'),
    url(r'^listen/(?P<book_id>\d+)/$', views.Listen.as_view()),
    url(r'^mp3/(?P<mp3_id>\d+)/$', views.Mp3.as_view()),
    url(r'^uploads/$', views.list_file, name='uploads'),
    url(r'torrent/add$', views.TorrentFileUploadView.as_view(),
        name='add-torrent'),
    url(r'^book/add/(?P<file_name>[0-9a-f]+)/$',
        views.AudioBookCreateView.as_view(), name='book-add'),
]