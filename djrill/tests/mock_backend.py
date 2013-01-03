from mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils import simplejson as json

class DjrillBackendMockAPITestCase(TestCase):
    """TestCase that uses Djrill EmailBackend with a mocked Mandrill API"""

    class MockResponse:
        """requests.post return value mock sufficient for DjrillBackend"""
        def __init__(self, status_code=200, content="{}"):
            self.status_code = status_code
            self.content = content

    def setUp(self):
        self.patch = patch('requests.post')
        self.mock_post = self.patch.start()
        self.mock_post.return_value = self.MockResponse()

        settings.MANDRILL_API_KEY = "FAKE_API_KEY_FOR_TESTING"

        # Django TestCase sets up locmem EmailBackend; override it here
        self.original_email_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

    def tearDown(self):
        self.patch.stop()
        settings.EMAIL_BACKEND = self.original_email_backend

    def get_api_call_data(self):
        """Returns the data posted to the Mandrill API.

        Fails test if API wasn't called.
        """
        if self.mock_post.call_args is None:
            raise AssertionError("Mandrill API was not called")
        (args, kwargs) = self.mock_post.call_args
        if 'data' not in kwargs:
            raise AssertionError("requests.post was called without data kwarg "
                                 "-- Maybe tests need to be updated for backend changes?")
        return json.loads(kwargs['data'])


