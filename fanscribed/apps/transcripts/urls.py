from django.conf.urls import patterns, url

from ...urls import LOGGED_IN_USER

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
        view=TaskAssignView.as_view(),
        kwargs=LOGGED_IN_USER),

)
