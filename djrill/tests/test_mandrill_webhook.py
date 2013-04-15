import json

from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

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

        def my_callback(sender, event_type, data, **kwargs):
            self.assertEqual(event_type, 'send')

        webhook_event.connect(my_callback)

        response = self.client.post('/webhook/?secret=abc123', {
            'mandrill_events': json.dumps([{"event": "send", "msg": {}}])
        })
        self.assertEqual(response.status_code, 200)
