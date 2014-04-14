from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
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

    url(r'^robots\.txt$',
        include('fanscribed.apps.robots.urls')),

    url(r'^accounts/signup/$',
        view=TemplateView.as_view(template_name='signup_closed.html')),

    url(r'^accounts/',
        include('allauth.urls')),

    url(r'^admin/',
        include(admin.site.urls)),

    url(r'^podcasts/',
        include('fanscribed.apps.podcasts.urls', 'podcasts'),
        kwargs=LOGGED_IN_USER),

    url(r'^profiles/',
        include('fanscribed.apps.profiles.urls', 'profiles')),

    url(r'^transcripts/',
        include('fanscribed.apps.transcripts.urls', 'transcripts'),
        kwargs=LOGGED_IN_USER),

    url(r'^$',
        name='home',
        view=TemplateView.as_view(template_name='home.html')),
)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
