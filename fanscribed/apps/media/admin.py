from django.contrib import admin

from .models import MediaFile


class MediaFileAdmin(admin.ModelAdmin):

    list_display = ('data_url',)


admin.site.register(MediaFile, MediaFileAdmin)
