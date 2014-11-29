from django.conf.urls import patterns, url

from . import views as v
from ...urls import LOGGED_IN_USER


urlpatterns = patterns(
    '',

    url(r'^(?P<pk>\d+)/$',
        name='detail',
        view=v.ProfileDetailView.as_view()),

    url(r'^edit/$',
        name='edit',
        view=v.ProfileUpdateView.as_view(),
        kwargs=LOGGED_IN_USER),
)
