from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import View

try:
    import requests
except ImportError:
    raise ImportError("Install the damn requirements!")


class DjrillIndexView(View):

    def get(self, request):
        #api_key = getattr(settings.MANDRILL_API_KEY, None)
        #api_url = getattr(settings.MANDRILL_API_URL)
        api_key = settings.MANDRILL_API_KEY or None
        api_url = settings.MANDRILL_API_URL or None
        if not api_key:
            raise ImproperlyConfigured("You have not set your mandrill api key "
                "in the settings file.")
        if not api_url:
            raise ImproperlyConfigured("You have not added the Mandrill api "
                "url to your settings.py")

        import pdb
        pdb.set_trace()
        r = requests.get("%susers/info.json" % api_url, data={"key": api_key})

        return HttpResponse(r)

def admin_list_view(request):
    return HttpResponse("Djrill Index")
