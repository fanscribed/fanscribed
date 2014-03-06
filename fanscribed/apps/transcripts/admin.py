from django.contrib import admin

from .models import Transcript, TranscriptMedia


class TranscriptAdmin(admin.ModelAdmin):

    list_display = ('name', 'length', 'created',)


class TranscriptMediaAdmin(admin.ModelAdmin):
    pass


admin.site.register(Transcript, TranscriptAdmin)
admin.site.register(TranscriptMedia, TranscriptMediaAdmin)
