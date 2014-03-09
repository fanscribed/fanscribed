from django.conf.urls import patterns, url

from vanilla import TemplateView


urlpatterns = patterns(
    '',

    url(r'^$',
        name='index',
        view=TemplateView.as_view(template_name='placeholder.html')),

    url(r'^register/$',
        name='register',
        view=TemplateView.as_view(template_name='placeholder.html')),
)
