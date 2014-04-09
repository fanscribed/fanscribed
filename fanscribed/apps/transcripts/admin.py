from django.contrib import admin

from . import models as m


class TranscriptAdmin(admin.ModelAdmin):

    list_display = ('name', 'length', 'created',)


class TranscriptMediaAdmin(admin.ModelAdmin):

    list_display = ('transcript', 'start', 'end',
                    'is_processed', 'is_full_length')


admin.site.register(m.Transcript, TranscriptAdmin)
admin.site.register(m.TranscriptMedia, TranscriptMediaAdmin)
