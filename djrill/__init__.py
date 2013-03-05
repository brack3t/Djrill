from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.utils.text import capfirst

from djrill.exceptions import MandrillAPIError, NotSupportedByMandrillError

from ._version import *

# This backend was developed against this API endpoint.
# You can override in settings.py, if desired.
MANDRILL_API_URL = getattr(settings, "MANDRILL_API_URL",
    "http://mandrillapp.com/api/1.0")

class DjrillAdminSite(AdminSite):
    index_template = "djrill/index.html"
    custom_views = []
    custom_urls = []

    def register_view(self, path, view, name, display_name=None):
        """Add a custom admin view.

        * `path` is the path in the admin where the view will live, e.g.
            http://example.com/admin/somepath
        * `view` is any view function you can imagine.
        * `name` is an optional pretty name for the list of custom views. If
            empty, we'll guess based on view.__name__.
        """
        self.custom_views.append((path, view, name, display_name))

    def register_url(self, path, view, name):
        self.custom_urls.append((path, view, name))

    def get_urls(self):
        """Add our custom views to the admin urlconf."""
        urls = super(DjrillAdminSite, self).get_urls()
        try:
            from django.conf.urls import include, patterns, url
        except ImportError:
            # Django 1.3
            #noinspection PyDeprecation
            from django.conf.urls.defaults import include, patterns, url
        for path, view, name, display_name in self.custom_views:
            urls += patterns('',
                url(r'^%s$' % path, self.admin_view(view), name=name),
            )
        for path, view, name in self.custom_urls:
            urls += patterns('',
                url(r'^%s$' % path, self.admin_view(view), name=name),
            )

        return urls

    def index(self, request, extra_context=None):
        """Make sure our list of custom views is on the index page."""
        if not extra_context:
            extra_context = {}
        custom_list = [(path, display_name if display_name else
            capfirst(view.__name__)) for path, view, name, display_name in
            self.custom_views]
        # Sort views alphabetically.
        custom_list.sort(key=lambda x: x[1])
        extra_context.update({
            'custom_list': custom_list
        })
        return super(DjrillAdminSite, self).index(request, extra_context)
