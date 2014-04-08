from django.contrib import admin

from .models import TranscriptMedia


class TranscriptMediaAdmin(admin.ModelAdmin):

    list_display = ('data_url',)


admin.site.register(TranscriptMedia, TranscriptMediaAdmin)
