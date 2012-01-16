from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils import simplejson as json
from django.views.generic import View

try:
    import requests
except ImportError:
    raise ImportError("Install the damn requirements!")


class DjrillApiMixin(object):
    """
    Simple Mixin to grab the api info from the settings file.
    """
    def __init__(self, *args, **kwargs):
        self.api_key = getattr(settings, "MANDRILL_API_KEY", None)
        self.api_url = getattr(settings, "MANDRILL_API_URL", None)

        if not self.api_key:
            raise ImproperlyConfigured("You have not set your mandrill api key "
                "in the settings file.")
        if not self.api_url:
            raise ImproperlyConfigured("You have not added the Mandrill api "
                "url to your settings.py")


class DjrillIndexView(DjrillApiMixin, View):

    def get(self, request):

        payload = json.dumps({"key": self.api_key})
        r = requests.post("%s/users/info.json" % self.api_url, data=payload)

        return HttpResponse(r.content)
