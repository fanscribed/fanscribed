"""Production settings and globals."""

from .base import *


# AUTH
# ----

THIRD_PARTY_APPS += (
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email'],
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': False,
    },
    'google': {
        'SCOPE': ['https://www.googleapis.com/auth/userinfo.profile',
                  'https://www.googleapis.com/auth/userinfo.email'],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    },
}


# ALLOWED HOSTS
# -------------

ALLOWED_HOSTS = environ['ALLOWED_HOSTS'].split(',')


# ADMINS
# ------

ADMINS = tuple(
    ('Fanscribed Admin', email)
    for email
    in environ['ADMIN_EMAILS'].split(','),
)


# EMAIL
# -----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'your_email@example.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER

# See: https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = get_env_setting('DEFAULT_FROM_EMAIL')


# DATABASE
# --------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_setting('DATABASE_NAME'),
        'USER': get_env_setting('DATABASE_USER'),
        'PASSWORD': get_env_setting('DATABASE_PASSWORD'),
        'HOST': get_env_setting('DATABASE_HOST'),
        'PORT': None,
    },
}


# CACHE
# -----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': get_env_setting('REDIS_CACHE_LOCATION'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': get_env_setting('REDIS_CACHE_PASSWORD')
        },
    },
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


# SECRET
# ------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_setting('SECRET_KEY')


# ROLLBAR
# -------

ROLLBAR['environment'] = 'production'


# MAILCHIMP
# ---------

MAILCHIMP_API_KEY = get_env_setting('MAILCHIMP_API_KEY')
MAILCHIMP_LIST_ID = get_env_setting('MAILCHIMP_LIST_ID')


# CELERY
# ------

BROKER_URL = get_env_setting('BROKER_URL')


# TRANSCRIPTION
# -------------

TRANSCRIPT_FRAGMENT_LENGTH = Decimal(get_env_setting('TRANSCRIPT_FRAGMENT_LENGTH'))
