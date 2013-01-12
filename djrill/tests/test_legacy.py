# Tests deprecated Djrill features

from django.test import TestCase

from djrill.mail import DjrillMessage
from djrill import MandrillAPIError, NotSupportedByMandrillError


class DjrillMessageTests(TestCase):
    """Test the DjrillMessage class (deprecated as of Djrill v0.2.0)

    Maintained for compatibility with older code.

    """

    def setUp(self):
        self.subject = "Djrill baby djrill."
        self.from_name = "Tarzan"
        self.from_email = "test@example"
        self.to = ["King Kong <kingkong@example.com>",
                   "Cheetah <cheetah@example.com", "bubbles@example.com"]
        self.text_content = "Wonderful fallback text content."
        self.html_content = "<h1>That's a nice HTML email right there.</h1>"
        self.headers = {"Reply-To": "tarzan@example.com"}
        self.tags = ["track", "this"]

    def test_djrill_message_success(self):
        msg = DjrillMessage(self.subject, self.text_content, self.from_email,
            self.to, tags=self.tags, headers=self.headers,
            from_name=self.from_name)

        self.assertIsInstance(msg, DjrillMessage)
        self.assertEqual(msg.body, self.text_content)
        self.assertEqual(msg.recipients(), self.to)
        self.assertEqual(msg.tags, self.tags)
        self.assertEqual(msg.extra_headers, self.headers)
        self.assertEqual(msg.from_name, self.from_name)

    def test_djrill_message_html_success(self):
        msg = DjrillMessage(self.subject, self.text_content, self.from_email,
            self.to, tags=self.tags)
        msg.attach_alternative(self.html_content, "text/html")

        self.assertEqual(msg.alternatives[0][0], self.html_content)

    def test_djrill_message_tag_failure(self):
        with self.assertRaises(ValueError):
            DjrillMessage(self.subject, self.text_content, self.from_email,
                self.to, tags=["_fail"])

    def test_djrill_message_tag_skip(self):
        """
        Test that tags over 50 chars are not included in the tags list.
        """
        tags = ["works", "awesomesauce",
                "iwilltestmycodeiwilltestmycodeiwilltestmycodeiwilltestmycode"]
        msg = DjrillMessage(self.subject, self.text_content, self.from_email,
            self.to, tags=tags)

        self.assertIsInstance(msg, DjrillMessage)
        self.assertIn(tags[0], msg.tags)
        self.assertIn(tags[1], msg.tags)
        self.assertNotIn(tags[2], msg.tags)

    def test_djrill_message_no_options(self):
        """DjrillMessage with only basic EmailMessage options should work"""
        msg = DjrillMessage(self.subject, self.text_content,
            self.from_email, self.to) # no Mandrill-specific options

        self.assertIsInstance(msg, DjrillMessage)
        self.assertEqual(msg.body, self.text_content)
        self.assertEqual(msg.recipients(), self.to)
        self.assertFalse(hasattr(msg, 'tags'))
        self.assertFalse(hasattr(msg, 'from_name'))
        self.assertFalse(hasattr(msg, 'preserve_recipients'))


class DjrillLegacyExceptionTests(TestCase):
    def test_DjrillBackendHTTPError(self):
        """MandrillApiError was DjrillBackendHTTPError in 0.2.0"""
        # ... and had to be imported from deep in the package:
        from djrill.mail.backends.djrill import DjrillBackendHTTPError
        ex = MandrillAPIError("testing")
        self.assertIsInstance(ex, DjrillBackendHTTPError)

    def test_NotSupportedByMandrillError(self):
        """Unsupported features used to just raise ValueError in 0.2.0"""
        ex = NotSupportedByMandrillError("testing")
        self.assertIsInstance(ex, ValueError)
