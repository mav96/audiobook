from django.conf.urls import url
from audiobooks import views


urlpatterns = [
    url(r'^$', views.HomePageView.as_view(),  name='index'),
    url(r'^listen/(?P<book_id>\d+)/$', views.Listen.as_view()),
    url(r'^mp3/(?P<mp3_id>\d+)/$', views.Mp3.as_view()),
    url(r'^search-form/$', views.SearchForm.as_view()),
    url(r'^search/$', views.Search.as_view()),
    url(r'^uploads/$', views.list_file, name='uploads'),
    url(r'book/add/$', views.AudioBookCreateView.as_view(), name='book-add'),
]