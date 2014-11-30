import os

from .base import *

from dj_database_url import parse


TESTING = True

DEFAULT_DATABASE_URL = (
    'postgres://postgres@'
    '{DB_PORT_5432_TCP_ADDR}:{DB_PORT_5432_TCP_PORT}/postgres'
    .format(**os.environ)
)
DATABASE_URL = getenv('DATABASE_URL', DEFAULT_DATABASE_URL)
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

DEFAULT_TEST_REDIS_CACHE_LOCATION = (
    '{REDIS_PORT_6379_TCP_ADDR}:{REDIS_PORT_6379_TCP_PORT}:2'
    .format(**os.environ)
)
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': getenv('TEST_REDIS_CACHE_LOCATION', DEFAULT_TEST_REDIS_CACHE_LOCATION),
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            'PASSWORD': getenv('TEST_REDIS_CACHE_PASSWORD', None),
        },
    },
}
