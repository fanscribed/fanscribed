"""Development settings and globals."""

import os

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
DEFAULT_DATABASE_URL = (
    'postgres://postgres@'
    '{DB_PORT_5432_TCP_ADDR}:{DB_PORT_5432_TCP_PORT}/postgres'
    .format(**os.environ)
)
DATABASE_URL = getenv('DATABASE_URL', DEFAULT_DATABASE_URL)
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL),
}


# CACHE
# -----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
DEFAULT_REDIS_CACHE_LOCATION = (
    '{REDIS_PORT_6379_TCP_ADDR}:{REDIS_PORT_6379_TCP_PORT}:1'
    .format(**os.environ)
)
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': getenv('REDIS_CACHE_LOCATION', DEFAULT_REDIS_CACHE_LOCATION),
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            'PASSWORD': getenv('REDIS_CACHE_PASSWORD', None),
        },
    },
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


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


# SUPERVISOR
# ----------

# Watchdog's inotify observer does not detect changes to files
# made on the host and exposed to the Linux VM via VMware's HGFS.
# Therefore, we must use the polling autoreloader.
SUPERVISOR_AUTORELOAD_POLL_ONLY = True
SUPERVISOR_AUTORELOAD_TIMEOUT = 5


# TOOLBAR
# -------

def debug_toolbar_any_host(request):
    from django.conf import settings
    return settings.DEBUG and not request.is_ajax()

INSTALLED_APPS += (
    'debug_toolbar',
)

DEBUG_TOOLBAR_CONFIG = dict(
    SHOW_TOOLBAR_CALLBACK='fanscribed.settings.local.debug_toolbar_any_host',
)
