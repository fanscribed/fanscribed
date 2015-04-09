from django.conf.urls import patterns, url

from ...urls import LOGGED_IN_USER
from . import views


urlpatterns = patterns(
    '',

    url(r'^$',
        name='index',
        view=views.TranscriptListView.as_view()),

    url(r'^(?P<pk>\d+)/$',
        name='detail',
        view=views.TranscriptDetailView.as_view()),

    url(r'^(?P<pk>\d+)-(?P<slug>[\w-]+)/$',
        name='detail_slug',
        view=views.TranscriptDetailView.as_view()),

    url(r'^(?P<transcript_pk>\d+)/tasks/(?P<type>\w+)/(?P<pk>\d+)/$',
        name='task_perform',
        view=views.TaskPerformView.as_view(),
        kwargs=LOGGED_IN_USER),

    url(r'^(?P<transcript_pk>\d+)/tasks/(?P<type>\w+)/(?P<pk>\d+)/audio/$',
        name='task_audio',
        view=views.TaskAudioView.as_view(),
        kwargs=LOGGED_IN_USER),

    url(r'^(?P<pk>\d+)/tasks/assign/$',
        name='task_assign',
        view=views.TaskAssignView.as_view(),
        kwargs=LOGGED_IN_USER),

)
