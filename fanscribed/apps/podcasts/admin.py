from django.contrib import admin

from .models import Podcast


class PodcastAdmin(admin.ModelAdmin):

    list_display = ('rss_url',)


class EpisodeAdmin(admin.ModelAdmin):

    list_display = ('podcast', 'title',)


class RssFetchAdmin(admin.ModelAdmin):

    list_display = ('podcast', 'state',)


admin.site.register(Podcast, PodcastAdmin)
