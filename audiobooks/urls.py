from django.conf.urls import url
from audiobooks import views

urlpatterns = [
    url(r'^$', views.HomePageView.as_view()),
    url(r'^listen/(?P<book_id>\d+)/$', views.Listen.as_view()),
    url(r'^mp3/(?P<mp3_id>\d+)/$', views.Mp3.as_view()),
    url(r'^search-form/$', views.Search_form.as_view()),
    url(r'^search/$', views.Search.as_view()),

]