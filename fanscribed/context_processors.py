from django.conf import settings
from django.contrib.sites.models import Site


def allow_signups(request):
    return {
        'ACCOUNT_ALLOW_SIGNUPS': settings.ACCOUNT_ALLOW_SIGNUPS,
    }


def debug(request):
    return {
        'DEBUG': settings.DEBUG,
        'TEMPLATE_DEBUG': settings.TEMPLATE_DEBUG,
    }


def analytics(request):
    if not request.user.is_superuser:
        return {
            'PIWIK_HOST': settings.PIWIK_HOST,
            'PIWIK_SITE_ID': settings.PIWIK_SITE_ID,
            'GOOGLE_ANALYTICS_DOMAIN': settings.GOOGLE_ANALYTICS_DOMAIN,
            'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        }
    else:
        return {}


def rollbar(request):
    return {
        'ROLLBAR_CLIENT_ACCESS_TOKEN': settings.ROLLBAR_CLIENT_ACCESS_TOKEN,
        'ROLLBAR_ENVIRONMENT': settings.ROLLBAR['environment'],
    }


def site(request):
    return {'site': Site.objects.get_current()}
