from django.contrib import admin

from .models import TranscriptMedia


class TranscriptMediaAdmin(admin.ModelAdmin):

    list_display = ('transcript', 'start', 'end',
                    'is_processed', 'is_full_length')


admin.site.register(TranscriptMedia, TranscriptMediaAdmin)
