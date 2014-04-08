from django.contrib import admin

from . import models as m


class TranscriptAdmin(admin.ModelAdmin):

    list_display = ('name', 'length', 'created',)


admin.site.register(m.Transcript, TranscriptAdmin)
