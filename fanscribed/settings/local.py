"""Development settings and globals."""

import dj_database_url

from .base import *


# DEBUG
# -----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG

TEMPLATE_CONTEXT_PROCESSORS += (
    'fanscribed.context_processors.debug',
)


# EMAIL
# -----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# DATABASE
# --------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASE_URL = getenv('DATABASE_URL', 'postgres://fanscribed:fanscribed@localhost:5432/fanscribed')
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL),
}


# CACHE
# -----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


# DEBUGGER RUNSERVER
# ------------------

INSTALLED_APPS += (
    'werkzeug_debugger_runserver',
)


# STORAGE
# -------

DEFAULT_FILE_STORAGE = 'storages.backends.overwrite.OverwriteStorage'


# AUTH
# ----

ACCOUNT_ALLOW_SIGNUPS = True


# TODO: reinstall the toolbar after figuring out how to avoid conflict with waffle

# # TOOLBAR
# # -------
#
# # See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
# INSTALLED_APPS += (
#     'debug_toolbar',
# )
#
# # See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
# INTERNAL_IPS = ('127.0.0.1',)
#
# # See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
# MIDDLEWARE_CLASSES += (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# )
