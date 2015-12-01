import hashlib
import hmac
import json
from base64 import b64encode

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .compat import b
from .signals import webhook_event


class DjrillWebhookSecretMixin(object):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        secret = getattr(settings, 'DJRILL_WEBHOOK_SECRET', None)
        secret_name = getattr(settings, 'DJRILL_WEBHOOK_SECRET_NAME', 'secret')

        if secret is None:
            raise ImproperlyConfigured(
                "You have not set DJRILL_WEBHOOK_SECRET in the settings file.")

        if request.GET.get(secret_name) != secret:
            return HttpResponse(status=403)

        return super(DjrillWebhookSecretMixin, self).dispatch(
            request, *args, **kwargs)


class DjrillWebhookSignatureMixin(object):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):

        signature_key = getattr(settings, 'DJRILL_WEBHOOK_SIGNATURE_KEY', None)

        if signature_key and request.method == "POST":

            # Make webhook url an explicit setting to make sure that this is the exact same string
            # that the user entered in Mandrill
            post_string = getattr(settings, "DJRILL_WEBHOOK_URL", None)
            if post_string is None:
                raise ImproperlyConfigured(
                    "You have set DJRILL_WEBHOOK_SIGNATURE_KEY, but haven't set DJRILL_WEBHOOK_URL in the settings file.")

            signature = request.META.get("HTTP_X_MANDRILL_SIGNATURE", None)
            if not signature:
                return HttpResponse(status=403, content="X-Mandrill-Signature not set")

            # The querydict is a bit special, see https://docs.djangoproject.com/en/dev/ref/request-response/#querydict-objects
            # Mandrill needs it to be sorted and added to the hash
            post_lists = sorted(request.POST.lists())
            for value_list in post_lists:
                for item in value_list[1]:
                    post_string += "%s%s" % (value_list[0], item)

            hash_string = b64encode(hmac.new(key=b(signature_key), msg=b(post_string), digestmod=hashlib.sha1).digest())
            if signature != hash_string:
                return HttpResponse(status=403, content="Signature doesn't match")

        return super(DjrillWebhookSignatureMixin, self).dispatch(
            request, *args, **kwargs)


class DjrillWebhookView(DjrillWebhookSecretMixin, DjrillWebhookSignatureMixin, View):
    def head(self, request, *args, **kwargs):
        return HttpResponse()

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.POST.get('mandrill_events'))
        except TypeError:
            return HttpResponse(status=400)

        for event in data:
            webhook_event.send(
                sender=None, event_type=event['event'], data=event)

        return HttpResponse()
