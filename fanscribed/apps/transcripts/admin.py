from django.contrib import admin

from .models import Transcript


class TranscriptAdmin(admin.ModelAdmin):

    list_display = ('name', 'length', 'created',)


admin.site.register(Transcript, TranscriptAdmin)
