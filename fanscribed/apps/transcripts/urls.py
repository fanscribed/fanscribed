from django.conf.urls import patterns, url

from .views import TranscriptList


urlpatterns = patterns(
    '',

    url(r'^$',
        name='index',
        view=TranscriptList.as_view()),

)
