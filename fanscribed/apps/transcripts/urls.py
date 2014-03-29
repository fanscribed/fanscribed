from django.conf.urls import patterns, url

from .views import TranscriptDetail, TranscriptList


urlpatterns = patterns(
    '',

    url(r'^$',
        name='index',
        view=TranscriptList.as_view()),

    url(r'^(?P<pk>\d+)/$',
        name='detail',
        view=TranscriptDetail.as_view()),

)
