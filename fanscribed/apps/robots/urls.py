from django.conf.urls import patterns, url

from .views import RobotsTxtView


urlpatterns = patterns(
    '',

    url(r'^$',
        name='txt',
        view=RobotsTxtView.as_view()),
)
