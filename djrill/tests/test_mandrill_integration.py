from __future__ import unicode_literals

import os
import unittest

from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

from djrill import MandrillAPIError


MANDRILL_TEST_API_KEY = os.getenv('MANDRILL_TEST_API_KEY')


@unittest.skipUnless(MANDRILL_TEST_API_KEY,
            "Set MANDRILL_TEST_API_KEY environment variable to run integration tests")
@override_settings(MANDRILL_API_KEY=MANDRILL_TEST_API_KEY,
                   EMAIL_BACKEND="djrill.mail.backends.djrill.DjrillBackend")
class DjrillIntegrationTests(TestCase):
    """Mandrill API integration tests

    These tests run against the **live** Mandrill API, using the
    environment variable `MANDRILL_TEST_API_KEY` as the API key.
    If that variable is not set, these tests won't run.

    See https://mandrill.zendesk.com/hc/en-us/articles/205582447
    for info on Mandrill test keys.

    """

    def setUp(self):
        self.message = mail.EmailMultiAlternatives(
            'Subject', 'Text content', 'from@example.com', ['to@example.com'])
        self.message.attach_alternative('<p>HTML content</p>', "text/html")

    def test_send_mail(self):
        # Example of getting the Mandrill send status and _id from the message
        sent_count = self.message.send()
        self.assertEqual(sent_count, 1)
        # noinspection PyUnresolvedReferences
        response = self.message.mandrill_response
        self.assertIn(response[0]['status'], ['sent', 'queued'])  # successful send (could still bounce later)
        self.assertEqual(response[0]['email'], 'to@example.com')
        self.assertGreater(len(response[0]['_id']), 0)

    def test_invalid_from(self):
        # Example of trying to send from an invalid address
        # Mandrill returns a 500 response (which raises a MandrillAPIError)
        self.message.from_email = 'webmaster@localhost'  # Django default DEFAULT_FROM_EMAIL
        try:
            self.message.send()
            self.fail("This line will not be reached, because send() raised an exception")
        except MandrillAPIError as err:
            self.assertEqual(err.status_code, 500)
            self.assertIn("email address is invalid", str(err))

    def test_invalid_to(self):
        # Example of detecting when a recipient is not a valid email address
        self.message.to = ['invalid@localhost']
        sent_count = self.message.send()
        self.assertEqual(sent_count, 1)  # The send call is "successful"...
        # noinspection PyUnresolvedReferences
        response = self.message.mandrill_response
        if response[0]['status'] == 'queued':
            self.skipTest("Mandrill queued the send -- can't complete this test")
        self.assertEqual(response[0]['status'], 'invalid')  # ... but the mail is not delivered

    def test_rejected_to(self):
        # Example of detecting when a recipient is on Mandrill's rejection blacklist
        self.message.to = ['reject@test.mandrillapp.com']
        sent_count = self.message.send()
        self.assertEqual(sent_count, 1)  # The send call is "successful"...
        # noinspection PyUnresolvedReferences
        response = self.message.mandrill_response
        if response[0]['status'] == 'queued':
            self.skipTest("Mandrill queued the send -- can't complete this test")
        self.assertEqual(response[0]['status'], 'rejected')  # ... but the mail is not delivered
        self.assertEqual(response[0]['reject_reason'], 'test')  # ... and here's why

    @override_settings(MANDRILL_API_KEY="Hey, that's not an API key!")
    def test_invalid_api_key(self):
        # Example of trying to send with an invalid MANDRILL_API_KEY
        try:
            self.message.send()
            self.fail("This line will not be reached, because send() raised an exception")
        except MandrillAPIError as err:
            self.assertEqual(err.status_code, 500)
            self.assertIn("Invalid API key", str(err))
