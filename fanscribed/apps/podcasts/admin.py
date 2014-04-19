from django.contrib import admin

from . import models as m


class EpisodeAdmin(admin.ModelAdmin):

    list_display = ('podcast', 'title', 'published',
                    'transcript', 'external_transcript')
    ordering = ('podcast', '-published')
    readonly_fields = ('podcast', 'guid', 'published')


# ---


class TranscriptionApprovalInline(admin.StackedInline):

    model = m.TranscriptionApproval
    fields = ('approval_type', 'notes')
    extra = 1


class PodcastAdmin(admin.ModelAdmin):

    actions = ['fetch']
    fields = ('rss_url',)
    list_display = ('title', 'link_url', 'rss_url')
    inlines = [
        TranscriptionApprovalInline,
    ]

    def fetch(self, request, queryset):
        fetched = 0
        for podcast in queryset:
            rss_fetch = m.RssFetch.objects.create(podcast=podcast)
            rss_fetch.start()
            fetched += 1
        message = 'fetched: {fetched}'
        self.message_user(request, message.format(**locals()))
    fetch.short_description = 'Fetch RSS for selected podcasts'


# ---


class RssFetchAdmin(admin.ModelAdmin):

    actions = ['start_fetch']
    list_display = ('podcast', 'fetched', 'state')

    def start_fetch(self, request, queryset):
        started = 0
        could_not_start = 0
        for rss_fetch in queryset:
            if rss_fetch.state == 'not_fetched':
                started += 1
                rss_fetch.start()
            else:
                could_not_start += 1
        message = 'started: {started}, could not start: {could_not_start}'
        self.message_user(request, message.format(**locals()))
    start_fetch.short_description = 'Start selected RSS fetches'


admin.site.register(m.Episode, EpisodeAdmin)
admin.site.register(m.Podcast, PodcastAdmin)
admin.site.register(m.RssFetch, RssFetchAdmin)
