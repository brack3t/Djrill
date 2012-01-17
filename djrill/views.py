from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import simplejson as json
from django.views.generic import TemplateView, View

try:
    import requests
except ImportError:
    raise ImportError("Install the damn requirements!")


class DjrillAdminMedia(object):
    def _media(self):
        js = ["js/core.js", "js/jquery.min.js", "js/jquery.init.js"]

        return forms.Media(js=["%s%s" % (settings.ADMIN_MEDIA_PREFIX, url)
            for url in js])
    media = property(_media)


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


class DjrillApiJsonObjectsMixin(object):
    """
    Mixin to grab json objects from the api.
    """
    api_uri = None

    def get_json_objects(self):
        payload = json.dumps({"key": self.api_key})
        req = requests.post("%s/%s" % (self.api_url, self.api_uri),
            data=payload)
        if req.status_code == 200:
            return req.content
        raise Exception("OH GOD, NO!")


class DjrillIndexView(DjrillApiMixin, TemplateView):
    template_name = "djrill/status.html"

    def get(self, request):

        payload = json.dumps({"key": self.api_key})
        req = requests.post("%s/users/info.json" % self.api_url, data=payload)

        return self.render_to_response({"status": json.loads(req.content)})


class DjrillSendersListView(DjrillAdminMedia, DjrillApiMixin,
    DjrillApiJsonObjectsMixin, TemplateView):

    api_uri = "users/senders.json"
    template_name = "djrill/senders_list.html"

    def get(self, request):
        objects = self.get_json_objects()
        return self.render_to_response({
            "objects": json.loads(objects),
            "media": self.media
        })


class DjrillDisableSenderView(DjrillApiMixin, View):

    def post(self, request):
        email = request.POST.get("email", None)

        if email:
            payload = {
                "key": self.api_key,
                "email": email
            }
            req = requests.post("%s/users/disable-sender.json" % self.api_url,
                data=json.dumps(payload))

            if req.status_code == 200:
                return HttpResponse("success")

        return HttpResponseForbidden()
