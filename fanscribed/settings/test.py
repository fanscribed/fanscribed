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

# Set specifically to 5.00 and 1.50 for tests.
TRANSCRIPT_FRAGMENT_LENGTH = Decimal('5.00')
TRANSCRIPT_FRAGMENT_OVERLAP = Decimal('1.50')

# For most tests, don't worry about teamwork requirement when assigning tasks.
TRANSCRIPTS_REQUIRE_TEAMWORK = False

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': getenv('TEST_REDIS_CACHE_LOCATION', 'localhost:6379:2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            'PASSWORD': getenv('TEST_REDIS_CACHE_PASSWORD', None),
        },
    },
}

del ROLLBAR  # Don't report test errors
