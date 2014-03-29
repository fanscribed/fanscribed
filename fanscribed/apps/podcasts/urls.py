from django.conf.urls import patterns, url

from vanilla import TemplateView

from .views import PodcastList


urlpatterns = patterns(
    '',

    url(r'^$',
        name='index',
        view=PodcastList.as_view()),

    url(r'^register/$',
        name='register',
        view=TemplateView.as_view(template_name='placeholder.html'),
        kwargs={'login_required': True}),
)
