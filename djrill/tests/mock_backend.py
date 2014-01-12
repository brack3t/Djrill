import json
from mock import patch

from django.conf import settings
from django.test import TestCase


class DjrillBackendMockAPITestCase(TestCase):
    """TestCase that uses Djrill EmailBackend with a mocked Mandrill API"""

    class MockResponse:
        """requests.post return value mock sufficient for DjrillBackend"""
        def __init__(self, status_code=200, content="{}", json=['']):
            self.status_code = status_code
            self.content = content
            self._json = json

        def json(self):
            return self._json

    def setUp(self):
        self.patch = patch('requests.post', autospec=True)
        self.mock_post = self.patch.start()
        self.mock_post.return_value = self.MockResponse()

        settings.MANDRILL_API_KEY = "FAKE_API_KEY_FOR_TESTING"

        # Django TestCase sets up locmem EmailBackend; override it here
        self.original_email_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

    def tearDown(self):
        self.patch.stop()
        settings.EMAIL_BACKEND = self.original_email_backend

    def assert_mandrill_called(self, endpoint):
        """Verifies the (mock) Mandrill API was called on endpoint.

        endpoint is a Mandrill API, e.g., "/messages/send.json"
        """
        # This assumes the last (or only) call to requests.post is the
        # Mandrill API call of interest.
        if self.mock_post.call_args is None:
            raise AssertionError("Mandrill API was not called")
        (args, kwargs) = self.mock_post.call_args
        try:
            post_url = kwargs.get('url', None) or args[0]
        except IndexError:
            raise AssertionError("requests.post was called without an url (?!)")
        if not post_url.endswith(endpoint):
            raise AssertionError(
                "requests.post was not called on %s\n(It was called on %s)"
                % (endpoint, post_url))

    def get_api_call_data(self):
        """Returns the data posted to the Mandrill API.

        Fails test if API wasn't called.
        """
        if self.mock_post.call_args is None:
            raise AssertionError("Mandrill API was not called")
        (args, kwargs) = self.mock_post.call_args
        try:
            post_data = kwargs.get('data', None) or args[1]
        except IndexError:
            raise AssertionError("requests.post was called without data")
        return json.loads(post_data)


