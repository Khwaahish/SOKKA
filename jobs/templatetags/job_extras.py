from django import template

register = template.Library()


@register.filter
def split(value, sep=','):
    """Split a string by sep and return a list. Safe for empty values."""
    if value is None:
        return []
    try:
        return [p for p in value.split(sep) if p is not None]
    except Exception:
        return []


@register.filter
def trim(value):
    """Trim whitespace from string value."""
    if value is None:
        return ''
    return str(value).strip()
