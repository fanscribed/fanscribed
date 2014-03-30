def refresh(obj):
    """Reload an object from the database."""
    return obj.__class__._default_manager.get(pk=obj.pk)
