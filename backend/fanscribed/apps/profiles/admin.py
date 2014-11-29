from django.contrib import admin

from . import models as m


class ProfileAdmin(admin.ModelAdmin):

    readonly_fields = ('nickname_state',)


class TaskTypeAdmin(admin.ModelAdmin):

    list_display = ('order', 'name', 'description')


admin.site.register(m.Profile, ProfileAdmin)
admin.site.register(m.TaskType, TaskTypeAdmin)
