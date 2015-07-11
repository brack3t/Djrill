import json
from mock import patch
import requests
import six

from django.test import TestCase
from django.test.utils import override_settings


@override_settings(MANDRILL_API_KEY="FAKE_API_KEY_FOR_TESTING",
                   EMAIL_BACKEND="djrill.mail.backends.djrill.DjrillBackend")
class DjrillBackendMockAPITestCase(TestCase):
    """TestCase that uses Djrill EmailBackend with a mocked Mandrill API"""

    class MockResponse(requests.Response):
        """requests.post return value mock sufficient for DjrillBackend"""
        def __init__(self, status_code=200, raw=six.b("{}"), encoding='utf-8'):
            super(DjrillBackendMockAPITestCase.MockResponse, self).__init__()
            self.status_code = status_code
            self.encoding = encoding
            self.raw = six.BytesIO(raw)

    def setUp(self):
        self.patch = patch('requests.Session.post', autospec=True)
        self.mock_post = self.patch.start()
        self.mock_post.return_value = self.MockResponse()

    def tearDown(self):
        self.patch.stop()

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
            post_url = kwargs.get('url', None) or args[1]
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
            post_data = kwargs.get('data', None) or args[2]
        except IndexError:
            raise AssertionError("requests.post was called without data")
        return json.loads(post_data)


