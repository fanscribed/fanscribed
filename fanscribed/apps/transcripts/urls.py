from django.conf.urls import patterns, url

from ...urls import LOGGED_IN_USER

from .views import (
    TaskAssignView, TaskPerformView, TaskAudioView,
    TranscriptDetailView, TranscriptListView,
)


urlpatterns = patterns(
    '',

    url(r'^$',
        name='index',
        view=TranscriptListView.as_view()),

    url(r'^(?P<pk>\d+)/$',
        name='detail',
        view=TranscriptDetailView.as_view()),

    url(r'^(?P<transcript_pk>\d+)/tasks/(?P<type>\w+)/(?P<pk>\d+)/$',
        name='task_perform',
        view=TaskPerformView.as_view(),
        kwargs=LOGGED_IN_USER),

    url(r'^(?P<transcript_pk>\d+)/tasks/(?P<type>\w+)/(?P<pk>\d+)/audio/$',
        name='task_audio',
        view=TaskAudioView.as_view(),
        kwargs=LOGGED_IN_USER),

    url(r'^(?P<pk>\d+)/tasks/assign/$',
        name='task_assign',
        view=TaskAssignView.as_view(),
        kwargs=LOGGED_IN_USER),

)
