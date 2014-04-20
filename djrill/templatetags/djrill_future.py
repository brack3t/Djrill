# Future templatetags library that is also backwards compatible with
# older versions of Django (so long as Djrill's code is compatible
# with the future behavior).

from django import template

# Django 1.8 changes autoescape behavior in cycle tag.
# Djrill has been compatible with future behavior all along.
try:
    from django.templatetags.future import cycle
except ImportError:
    from django.template.defaulttags import cycle


register = template.Library()
register.tag(cycle)
