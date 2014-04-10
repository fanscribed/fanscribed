from django.conf.urls import patterns, url

from vanilla import TemplateView

from . import views as v


urlpatterns = patterns(
    '',

    # -- podcasts --------------------------------------

    url(r'^$',
        name='index',
        view=v.PodcastList.as_view()),

    url(r'^register/$',
        name='register',
        view=TemplateView.as_view(template_name='placeholder.html'),
        kwargs={'login_required': True}),

    url(r'^(?P<pk>\d+)/$',
        name='detail',
        view=v.PodcastDetail.as_view()),

    # -- episodes --------------------------------------

    url(r'^(?P<podcast_pk>\d+)/episodes/(?P<pk>\d+)/$',
        name='episode_detail',
        view=v.EpisodeDetail.as_view()),

    url(r'^(?P<podcast_pk>\d+)/episodes/(?P<pk>\d+)/create_transcript/$',
        name='episode_create_transcript',
        view=v.EpisodeCreateTranscript.as_view()),

)
