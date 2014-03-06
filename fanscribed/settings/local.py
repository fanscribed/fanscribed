"""Development settings and globals."""


from .base import *


# DEBUG
# -----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG


# EMAIL
# -----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# DATABASE
# --------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fanscribed',
        'USER': 'fanscribed',
        'PASSWORD': 'fanscribed',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# CACHE
# -----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


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
