"""Functions commonly used in other modules."""

from pyramid.threadlocal import get_current_registry


_settings = None


def app_settings():
    global _settings
    if _settings is None:
        _settings = get_current_registry().settings
    return _settings
