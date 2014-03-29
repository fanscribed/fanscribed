from django.conf.urls import patterns, url

from vanilla import TemplateView

from .views import EpisodeDetail, PodcastDetail, PodcastList


urlpatterns = patterns(
    '',

    # -- podcasts --------------------------------------

    url(r'^$',
        name='index',
        view=PodcastList.as_view()),

    url(r'^register/$',
        name='register',
        view=TemplateView.as_view(template_name='placeholder.html'),
        kwargs={'login_required': True}),

    url(r'^(?P<pk>\d+)/$',
        name='detail',
        view=PodcastDetail.as_view()),

    # -- episodes --------------------------------------

    url(r'^(?P<podcast_pk>\d+)/episodes/(?P<pk>\d+)/$',
        name='episode_detail',
        view=EpisodeDetail.as_view()),

)
