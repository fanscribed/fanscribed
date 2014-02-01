from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


# URL patterns used by all projects based on fanscribed core.
urlpatterns = patterns(
    '',
    url(r'^accounts/',
        include('allauth.urls')),

    url(r'^accounts/',
        include('fanscribed.apps.profiles.urls', 'profiles', 'profiles')),

    url(r'^admin/',
        include(admin.site.urls)),

    url(r'^$',
        name='home',
        view=TemplateView.as_view(template_name='home.html')),
)
