from .base import *


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

CELERY_ALWAYS_EAGER = True
