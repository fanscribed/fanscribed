from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


# Attach this to kwargs of an url to require login.
LOGGED_IN_USER = {
    'login_required': True,
}


# URL patterns used by all projects based on fanscribed core.
urlpatterns = patterns(
    '',

    url(r'^accounts/',
        include('allauth.urls')),

    url(r'^admin/',
        include(admin.site.urls)),

    url(r'^podcasts/',
        include('fanscribed.apps.podcasts.urls', 'podcasts')),

    url(r'^profiles/',
        include('fanscribed.apps.profiles.urls', 'profiles')),

    url(r'^transcripts/',
        include('fanscribed.apps.transcripts.urls', 'transcripts')),

    url(r'^$',
        name='home',
        view=TemplateView.as_view(template_name='home.html')),
)
