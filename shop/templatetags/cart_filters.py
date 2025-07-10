from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Dono values ko multiply karta hai (quantity * price)."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
@register.filter
def to_range(value, arg):
    """value se arg tak ki range return karta hai (inclusive start, exclusive end)."""
    return range(int(value), int(arg))

@register.filter
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0