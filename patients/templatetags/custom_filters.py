from django import template
import os

from django import template
import os

register = template.Library()

@register.filter
def filename(value):
    """Extract just the filename from a full path"""
    return os.path.basename(value)

@register.filter
def split(value, arg):
    """Split a string by the given argument"""
    return value.split(arg)

@register.filter
def filter_by_category(queryset, category):
    """Filter documents by category"""
    return [doc for doc in queryset if doc.category == category]