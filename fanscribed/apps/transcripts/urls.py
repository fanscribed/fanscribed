from django.conf.urls import patterns, url

from ...urls import LOGGED_IN_USER

from .views import (
    TaskAssignView, TaskPerformView,
    TranscriptDetailView, TranscriptListView,
    TranscriptTextView,
)


urlpatterns = patterns(
    '',

    url(r'^$',
        name='index',
        view=TranscriptListView.as_view()),

    url(r'^(?P<pk>\d+)/$',
        name='detail',
        view=TranscriptDetailView.as_view()),

    url(r'^(?P<pk>\d+)/text/$',
        name='text',
        view=TranscriptTextView.as_view()),

    url(r'^(?P<transcript_pk>\d+)/tasks/(?P<type>\w+)/(?P<pk>\d+)/$',
        name='task_perform',
        view=TaskPerformView.as_view(),
        kwargs=LOGGED_IN_USER),

    url(r'^(?P<pk>\d+)/tasks/assign/$',
        name='task_assign',
        view=TaskAssignView.as_view(),
        kwargs=LOGGED_IN_USER),

)
