from django.conf.urls import patterns, url

from .views import (
    TaskAssignView,
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

    url(r'^(?P<pk>\d+)/tasks/assign/$',
        name='task_assign',
        view=TaskAssignView.as_view()),

)
