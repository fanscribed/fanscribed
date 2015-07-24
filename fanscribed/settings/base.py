"""Common settings and globals."""

from decimal import Decimal
import os
from os import environ, getenv
from os.path import abspath, basename, dirname, join, normpath
import sys

import fanscribed


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(error_msg)


LOCAL_APPS = ()
THIRD_PARTY_APPS = ()


# PATH
# ----

# Absolute filesystem path to the Django project directory:
PACKAGE_ROOT = dirname(abspath(fanscribed.__file__))

# Site name:
SITE_NAME = basename(PACKAGE_ROOT)


# DEBUG
# -----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = bool(getenv('DEBUG', False))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG


# MANAGER
# -------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('Your Name', 'your_email@example.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS


# DATABASE
# --------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


# GENERAL
# -------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'America/Chicago'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
########## END GENERAL CONFIGURATION


# AWS
# ---

AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = getenv('AWS_STORAGE_BUCKET_NAME')


# MEDIA
# -----

if AWS_ACCESS_KEY_ID:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    # noinspection PyUnresolvedReferences
    MEDIA_ROOT = '/media/'
    MEDIA_URL = '//fanscribed.s3.amazonaws.com/media/'
else:
    MEDIA_ROOT = normpath(join(PACKAGE_ROOT, '..', 'media'))
    MEDIA_URL = '/media/'


# STATIC
# ------

STATIC_ROOT = normpath(join(PACKAGE_ROOT, 'assets'))
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    normpath(join(PACKAGE_ROOT, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# SECRET
# ------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = r"%w=+!*&s5d#gk4nd4^sc6_(5wc5-6kk9*$hx&g)*_s2k60v1ve"


# SITE
# ----

# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []


# TEMPLATE
# --------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'fanscribed.context_processors.site',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    normpath(join(PACKAGE_ROOT, 'templates')),
)


# MIDDLEWARE
# ----------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)


# URL
# ---

# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME


# LOGGING
# -------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


# WSGI
# ----

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'fanscribed.wsgi.application'


# AUTH / ACCOUNTS
# ---------------

MIDDLEWARE_CLASSES += (
    'fanscribed.middleware.LoginRequiredMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS += (
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
    'fanscribed.context_processors.allow_signups',
)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
THIRD_PARTY_APPS += (
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
)
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Fanscribed] '
ACCOUNT_USERNAME_REQUIRED = False
AUTH_PROFILE_MODEL = 'profiles.Profile'
LOGIN_REDIRECT_URL = 'home'
ACCOUNT_ALLOW_SIGNUPS = (getenv('ACCOUNT_ALLOW_SIGNUPS', '0') == '1')


# CELERY
# ------

THIRD_PARTY_APPS += (
    'djcelery',
)
BROKER_URL = getenv('BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Used for local caching of media files for faster processing.
MEDIA_CACHE_PATH = join(PACKAGE_ROOT, '..', '.mediafile-cache')


# WAFFLE
# ------

THIRD_PARTY_APPS += (
    'waffle',
)
LOCAL_APPS += (
    'fanscribed.apps.waffle_extensions',
)
FEATURES_YAML = join(PACKAGE_ROOT, '..', 'waffle.yaml')
MIDDLEWARE_CLASSES += (
    'waffle.middleware.WaffleMiddleware',
)


# MAILCHIMP
# ---------

MAILCHIMP_API_KEY = ''  # Set this in .production based on env vars
MAILCHIMP_LIST_ID = ''  # Set this in .production based on env vars


# SHELL_PLUS
# ----------

IPYTHON_ARGUMENTS = [
    '--ext', 'django_extensions.management.notebook_extension',
    '--ip=0.0.0.0',
    '--no-browser',
]


# TRANSCRIPTION
# -------------

TRANSCRIPT_FRAGMENT_LENGTH = Decimal('5.00')
TRANSCRIPT_FRAGMENT_OVERLAP = Decimal('1.00')
TRANSCRIPTS_REQUIRE_TEAMWORK = True


# TESTING
# -------

TESTING = False


# MEDIA CONVERSION
# ----------------

if sys.platform == 'linux2':

    MP3SPLT_PATH = getenv('MP3SPLT_PATH', '/usr/bin/mp3splt')
    AVPROBE_PATH = getenv('AVPROBE_PATH', '/usr/bin/avprobe')
    AVCONV_PATH = getenv('AVCONV_PATH', '/usr/bin/avconv')

elif sys.platform == 'darwin':

    # $ brew install mp3splt ffmpeg
    MP3SPLT_PATH = getenv('MP3SPLT_PATH', '/usr/local/bin/mp3splt')
    AVPROBE_PATH = getenv('AVPROBE_PATH', '/usr/local/bin/ffprobe')
    AVCONV_PATH = getenv('AVCONV_PATH', '/usr/local/bin/ffmpeg')


# ANALYTICS
# ---------

PIWIK_HOST = getenv('PIWIK_HOST')
PIWIK_SITE_ID = getenv('PIWIK_SITE_ID')

GOOGLE_ANALYTICS_DOMAIN = getenv('GOOGLE_ANALYTICS_DOMAIN')
GOOGLE_ANALYTICS_ID = getenv('GOOGLE_ANALYTICS_ID')

TEMPLATE_CONTEXT_PROCESSORS += (
    'fanscribed.context_processors.analytics',
)


# API
# ---

THIRD_PARTY_APPS += (
    'rest_framework',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    ),
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,
}


# ROLLBAR
# -------

MIDDLEWARE_CLASSES += (
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
)

ROLLBAR = {
    'access_token': getenv('ROLLBAR_SERVER_ACCESS_TOKEN'),
    'environment': None, # set in local.py and production.py
    'branch': 'master',
    'root': abspath(join(PACKAGE_ROOT, '..')),
}

ROLLBAR_CLIENT_ACCESS_TOKEN = getenv('ROLLBAR_CLIENT_ACCESS_TOKEN')

TEMPLATE_CONTEXT_PROCESSORS += (
    'fanscribed.context_processors.rollbar',
)


# JS_HOST
# -------

# if 'NO_JSHOST' not in os.environ:
#     THIRD_PARTY_APPS += (
#         'js_host',
#     )
#
# JS_HOST = {
#     'SOURCE_ROOT': abspath(join(PACKAGE_ROOT, '..')),
#     'USE_MANAGER': False,
# }


# WEBPACK
# -------

THIRD_PARTY_APPS += (
    'webpack',
)

STATICFILES_FINDERS += (
    'webpack.django_integration.WebpackFinder',
)

WEBPACK = {
    'BUILD_URL': getenv('WEBPACK_BUILD_URL', 'http://localhost:7779/build'),
    'STATIC_ROOT': STATIC_ROOT,
    'STATIC_URL': STATIC_URL,
    'WATCH': DEBUG,
    'HMR': DEBUG,
    'CONFIG_DIRS': PACKAGE_ROOT,
    'CONTEXT': {
        'DEBUG': DEBUG,
    },
}

WEBPACK_CONFIG_FILE = os.path.join(PACKAGE_ROOT, '..', 'fanscribed.webpack.js')


# REACT
# -----

THIRD_PARTY_APPS += (
    'react',
)

REACT = {
    'RENDER': True,
    'RENDER_URL': getenv('REACT_RENDER_URL', 'http://localhost:7778/render'),
}


# APPS
# ----

DJANGO_APPS = (
    # Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # Admin:
    'django.contrib.admin',
)
THIRD_PARTY_APPS += (
    'bootstrap3',
    'django_extensions',
    'django_object_actions',
    'djsupervisor',
    'storages',
)
# Apps specific for this project go here.
LOCAL_APPS += (
    'fanscribed',                   # Templates and static files.
    'fanscribed.apps.mailinglist',  # Mailing list subscriptions.
    'fanscribed.apps.media',        # Media file handling.
    'fanscribed.apps.podcasts',     # Podcasts and episodes.
    'fanscribed.apps.profiles',     # Accounts and profiles.
    'fanscribed.apps.robots',       # robots.txt management.
    'fanscribed.apps.transcripts',  # The transcription engine.
)
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
