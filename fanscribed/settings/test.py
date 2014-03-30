from .base import *


TESTING = True

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

BROKER_BACKEND = 'memory'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# Set specifically to 5.00 for tests.
TRANSCRIPT_FRAGMENT_LENGTH = Decimal('5.00')
