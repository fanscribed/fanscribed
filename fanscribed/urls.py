from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


# URL patterns used by all projects based on fanscribed core.
base_urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)


# URL patterns used by only this project.
urlpatterns = base_urlpatterns + patterns('',
    url(r'^$', TemplateView.as_view(template_name='index.html')),
)
