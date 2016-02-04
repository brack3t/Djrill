import hashlib
import hmac
import json
from base64 import b64encode

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from djrill.compat import b
from djrill.signals import webhook_event


class DjrillWebhookSecretMixinTests(TestCase):
    """
    Test mixin used in optional Mandrill webhook support
    """

    def test_missing_secret(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.get('/webhook/')

    @override_settings(DJRILL_WEBHOOK_SECRET='abc123')
    def test_incorrect_secret(self):
        response = self.client.head('/webhook/?secret=wrong')
        self.assertEqual(response.status_code, 403)

    @override_settings(DJRILL_WEBHOOK_SECRET='abc123')
    def test_default_secret_name(self):
        response = self.client.head('/webhook/?secret=abc123')
        self.assertEqual(response.status_code, 200)

    @override_settings(DJRILL_WEBHOOK_SECRET='abc123', DJRILL_WEBHOOK_SECRET_NAME='verysecret')
    def test_custom_secret_name(self):
        response = self.client.head('/webhook/?verysecret=abc123')
        self.assertEqual(response.status_code, 200)


@override_settings(DJRILL_WEBHOOK_SECRET='abc123',
                   DJRILL_WEBHOOK_SIGNATURE_KEY="signature")
class DjrillWebhookSignatureMixinTests(TestCase):
    """
    Test mixin used in optional Mandrill webhook signature support
    """

    def test_incorrect_settings(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.post('/webhook/?secret=abc123')

    @override_settings(DJRILL_WEBHOOK_URL="/webhook/?secret=abc123",
                       DJRILL_WEBHOOK_SIGNATURE_KEY = "anothersignature")
    def test_unauthorized(self):
        response = self.client.post(settings.DJRILL_WEBHOOK_URL)
        self.assertEqual(response.status_code, 403)

    @override_settings(DJRILL_WEBHOOK_URL="/webhook/?secret=abc123")
    def test_signature(self):
        signature = hmac.new(key=b(settings.DJRILL_WEBHOOK_SIGNATURE_KEY),
                             msg=b(settings.DJRILL_WEBHOOK_URL+"mandrill_events[]"),
                             digestmod=hashlib.sha1)
        hash_string = b64encode(signature.digest())
        response = self.client.post('/webhook/?secret=abc123', data={"mandrill_events":"[]"},
                                    **{"HTTP_X_MANDRILL_SIGNATURE": hash_string})
        self.assertEqual(response.status_code, 200)


@override_settings(DJRILL_WEBHOOK_SECRET='abc123')
class DjrillWebhookViewTests(TestCase):
    """
    Test optional Mandrill webhook view
    """

    def test_head_request(self):
        response = self.client.head('/webhook/?secret=abc123')
        self.assertEqual(response.status_code, 200)

    def test_post_request_invalid_json(self):
        response = self.client.post('/webhook/?secret=abc123')
        self.assertEqual(response.status_code, 400)

    def test_post_request_valid_json(self):
        response = self.client.post('/webhook/?secret=abc123', {
            'mandrill_events': json.dumps([{"event": "send", "msg": {}}])
        })
        self.assertEqual(response.status_code, 200)

    def test_webhook_send_signal(self):
        self.signal_received_count = 0
        test_event = {"event": "send", "msg": {}}

        def my_callback(sender, event_type, data, **kwargs):
            self.signal_received_count += 1
            self.assertEqual(event_type, 'send')
            self.assertEqual(data, test_event)

        try:
            webhook_event.connect(my_callback, weak=False)  # local callback func, so don't use weak ref
            response = self.client.post('/webhook/?secret=abc123', {
                'mandrill_events': json.dumps([test_event])
            })
        finally:
            webhook_event.disconnect(my_callback)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.signal_received_count, 1)

    def test_webhook_sync_event(self):
        # Mandrill sync events use a different format from other events
        # https://mandrill.zendesk.com/hc/en-us/articles/205583297-Sync-Event-Webhook-format
        self.signal_received_count = 0
        test_event = {"type": "whitelist", "action": "add"}

        def my_callback(sender, event_type, data, **kwargs):
            self.signal_received_count += 1
            self.assertEqual(event_type, 'whitelist_add')  # synthesized event_type
            self.assertEqual(data, test_event)

        try:
            webhook_event.connect(my_callback, weak=False)  # local callback func, so don't use weak ref
            response = self.client.post('/webhook/?secret=abc123', {
                'mandrill_events': json.dumps([test_event])
            })
        finally:
            webhook_event.disconnect(my_callback)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.signal_received_count, 1)
