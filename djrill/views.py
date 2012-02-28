from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import (HttpResponseForbidden, HttpResponseRedirect)
from django.utils import simplejson as json
from django.views.generic import TemplateView, View

from djrill.forms import CreateSenderForm

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

    def get_context_data(self, **kwargs):
        kwargs = super(DjrillApiMixin, self).get_context_data(**kwargs)

        status = False
        req = requests.post("%s/%s" % (self.api_url, "users/ping.json"),
            data={"key": self.api_key})
        if req.status_code == 200:
            status = True

        kwargs.update({"status": status})
        return kwargs


class DjrillApiJsonObjectsMixin(object):
    """
    Mixin to grab json objects from the api.
    """
    api_uri = None

    def get_api_uri(self):
        if self.api_uri is None:
            raise ImproperlyConfigured(u"%(cls)s is missing an api_uri. Define "
                u"%(cls)s.api_uri or override %(cls)s.get_api_uri()." % {
                    "cls": self.__class__.__name__
                })

    def get_json_objects(self, extra_dict=None, extra_api_uri=None):
        request_dict = {"key": self.api_key}
        if extra_dict:
            request_dict.update(extra_dict)
        payload = json.dumps(request_dict)
        api_uri = extra_api_uri or self.api_uri
        req = requests.post("%s/%s" % (self.api_url, api_uri),
            data=payload)
        if req.status_code == 200:
            return req.content
        messages.error(self.request, self._api_error_handler(req))
        return json.dumps("error")

    def _api_error_handler(self, req):
        """
        If the API returns an error, display it to the user.
        """
        content = json.loads(req.content)
        return "Mandrill returned a %d response: %s" % (req.status_code,
            content["message"])


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
        form = CreateSenderForm()
        objects = self.get_json_objects()
        context = self.get_context_data()
        context.update({
            "objects": json.loads(objects),
            "media": self.media,
            "form": form
        })

        return self.render_to_response(context)


class DjrillSenderView(DjrillApiMixin, View):
    api_action = None
    error_message = None
    success_message = None

    def post(self, request):
        email = request.POST.get("email", None)

        if email:
            payload = {
                "key": self.api_key,
                "email": email
            }
            req = requests.post("%s/%s" % (self.api_url, self.api_action),
                data=json.dumps(payload))

            if req.status_code == 200:
                messages.success(request, self.success_message)
            else:
                messages.error(request, self.error_message)
            return HttpResponseRedirect(reverse("admin:djrill_senders"))

        return HttpResponseForbidden()


class DjrillDisableSenderView(DjrillSenderView):
    api_action = "users/disable-sender.json"
    error_message = "Sender was not disabled."
    success_message = "Sender was disabled."


class DjrillVerifySenderView(DjrillSenderView):
    api_action = "users/verify-sender.json"
    error_message = "Sender was not verified."
    success_message = "Sender was verified."


class DjrillAddSenderView(DjrillVerifySenderView):
    error_message = "Sender was not added."
    success_message = "Sender was added."


class DjrillTagListView(DjrillAdminMedia, DjrillApiMixin,
    DjrillApiJsonObjectsMixin, TemplateView):

    api_uri = "tags/list.json"
    template_name = "djrill/tags_list.html"

    def get(self, request):
        objects = self.get_json_objects()
        context = self.get_context_data()
        context.update({
            "objects": json.loads(objects),
            "media": self.media,
        })
        return self.render_to_response(context)

class DjrillUrlListView(DjrillAdminMedia, DjrillApiMixin,
    DjrillApiJsonObjectsMixin, TemplateView):

    api_uri = "urls/list.json"
    template_name = "djrill/urls_list.html"

    def get(self, request):
        objects = self.get_json_objects()
        context = self.get_context_data()
        context.update({
            "objects": json.loads(objects),
            "media": self.media
        })
        return self.render_to_response(context)
