from base64 import b64encode
import hashlib
import hmac
import json

from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from ..compat import b
from ..signals import webhook_event


class DjrillWebhookSecretMixinTests(TestCase):
    """
    Test mixin used in optional Mandrill webhook support
    """

    def test_missing_secret(self):
        del settings.DJRILL_WEBHOOK_SECRET

        with self.assertRaises(ImproperlyConfigured):
            self.client.get('/webhook/')

    def test_incorrect_secret(self):
        settings.DJRILL_WEBHOOK_SECRET = 'abc123'

        response = self.client.head('/webhook/?secret=wrong')
        self.assertEqual(response.status_code, 403)

    def test_default_secret_name(self):
        del settings.DJRILL_WEBHOOK_SECRET_NAME
        settings.DJRILL_WEBHOOK_SECRET = 'abc123'

        response = self.client.head('/webhook/?secret=abc123')
        self.assertEqual(response.status_code, 200)

    def test_custom_secret_name(self):
        settings.DJRILL_WEBHOOK_SECRET = 'abc123'
        settings.DJRILL_WEBHOOK_SECRET_NAME = 'verysecret'

        response = self.client.head('/webhook/?verysecret=abc123')
        self.assertEqual(response.status_code, 200)


class DjrillWebhookSignatureMixinTests(TestCase):
    """
    Test mixin used in optional Mandrill webhook signature support
    """

    def setUp(self):
        settings.DJRILL_WEBHOOK_SECRET = 'abc123'
        settings.DJRILL_WEBHOOK_SIGNATURE_KEY = "signature"
        settings.DJRILL_WEBHOOK_URL = "/webhook/?secret=abc123"

    def test_incorrect_settings(self):
        del settings.DJRILL_WEBHOOK_URL
        with self.assertRaises(ImproperlyConfigured):
            self.client.post('/webhook/?secret=abc123')
        settings.DJRILL_WEBHOOK_URL = "/webhook/?secret=abc123"

    def test_unauthorized(self):
        settings.DJRILL_WEBHOOK_SIGNATURE_KEY = "anothersignature"
        response = self.client.post(settings.DJRILL_WEBHOOK_URL)
        self.assertEqual(response.status_code, 403)

    def test_signature(self):
        signature = hmac.new(key=b(settings.DJRILL_WEBHOOK_SIGNATURE_KEY), msg = b(settings.DJRILL_WEBHOOK_URL+"mandrill_events[]"), digestmod=hashlib.sha1)
        hash_string = b64encode(signature.digest())
        response = self.client.post('/webhook/?secret=abc123', data={"mandrill_events":"[]"}, **{"X-Mandrill-Signature" : hash_string})
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        del settings.DJRILL_WEBHOOK_SIGNATURE_KEY
        del settings.DJRILL_WEBHOOK_URL

class DjrillWebhookViewTests(TestCase):
    """
    Test optional Mandrill webhook view
    """

    def setUp(self):
        settings.DJRILL_WEBHOOK_SECRET = 'abc123'

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

        webhook_event.connect(my_callback)

        response = self.client.post('/webhook/?secret=abc123', {
            'mandrill_events': json.dumps([test_event])
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.signal_received_count, 1)
