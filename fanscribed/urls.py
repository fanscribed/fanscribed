from django.conf.urls import patterns, include, url

from fanscribed.apps.core.views import CoreIndexView


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


# URL patterns used by all projects based on fanscribed core.
base_urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

# URL patterns used by only this project.
core_urlpatterns = patterns('',
    url(r'^$', CoreIndexView.as_view(), name='home'),
)


urlpatterns = base_urlpatterns + core_urlpatterns
