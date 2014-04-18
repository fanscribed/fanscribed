import cgi

from django import template


register = template.Library()


@register.filter
def html_escape(string):
    return cgi.escape(string, quote=True)
