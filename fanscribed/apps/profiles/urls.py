from django.conf.urls import patterns, url

from . import views as v


urlpatterns = patterns(
    '',

    url(r'^(?P<pk>\d+)/$',
        name='detail',
        view=v.ProfileDetailView.as_view()),

    url(r'^edit/$',
        name='edit',
        view=v.ProfileUpdateView.as_view()),
)
