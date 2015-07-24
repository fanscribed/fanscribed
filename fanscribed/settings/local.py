"""Development settings and globals."""

import re
import os

import dj_database_url

# Set DEBUG before importing rest of config.
if not os.environ.get('NODEBUG', False):
    os.environ['DEBUG'] = '1'

from .base import *


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
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': getenv('REDIS_CACHE_LOCATION', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
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

def show_toolbar(request):
    from django.conf import settings
    if not settings.DEBUG or request.is_ajax():
        return False
    uri = request.get_full_path()
    # Don't show debug toolbar in admin or editor.
    if re.match(r'/(admin|editor)/', uri):
        return False
    return True


INSTALLED_APPS += (
    'debug_toolbar',
)

DEBUG_TOOLBAR_CONFIG = dict(
    SHOW_TOOLBAR_CALLBACK='fanscribed.settings.local.show_toolbar',
)


# ROLLBAR
# -------

ROLLBAR['environment'] = 'development'
