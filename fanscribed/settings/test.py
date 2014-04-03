from .base import *

from dj_database_url import parse


TESTING = True

DATABASE_URL = getenv('DATABASE_URL', 'postgres://fanscribed:fanscribed@localhost:5432/fanscribed')
DATABASES = {
    'default': parse(DATABASE_URL),
}

BROKER_BACKEND = 'memory'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# Set specifically to 5.00 for tests.
TRANSCRIPT_FRAGMENT_LENGTH = Decimal('5.00')
