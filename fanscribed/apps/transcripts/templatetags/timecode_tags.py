from django import template

from fanscribed.apps.media.timecode import decimal_to_timecode


register = template.Library()


@register.filter()
def timecode(value):
    return decimal_to_timecode(value)
