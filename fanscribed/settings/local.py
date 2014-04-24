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
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': getenv('REDIS_CACHE_LOCATION', 'localhost:6379:1'),
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
