import bleach
from django import template


register = template.Library()


DESCRIPTION_ALLOWED_TAGS = bleach.ALLOWED_TAGS + [
    'p',
]


@register.filter(is_safe=True)
def bleached_description(value):
    cleaned = bleach.clean(value, tags=DESCRIPTION_ALLOWED_TAGS, strip=True)
    linkified = bleach.linkify(cleaned)
    return linkified
