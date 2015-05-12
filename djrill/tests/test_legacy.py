# Tests deprecated Djrill features

from datetime import date, datetime
import warnings

from django.core import mail
from django.test import TestCase

from djrill import MandrillAPIError, NotSupportedByMandrillError, DjrillAdminSite
from djrill.mail import DjrillMessage
from djrill.tests.mock_backend import DjrillBackendMockAPITestCase
from djrill.tests.utils import reset_warning_registry


class DjrillBackendDeprecationTests(DjrillBackendMockAPITestCase):

    def setUp(self):
        reset_warning_registry()
        super(DjrillBackendDeprecationTests, self).setUp()

    def test_deprecated_admin_site(self):
        """Djrill 2.0 drops the custom DjrillAdminSite"""
        self.assertWarnsMessage(DeprecationWarning,
                                "DjrillAdminSite will be removed in Djrill 2.0",
                                DjrillAdminSite)

    def test_deprecated_json_date_encoding(self):
        """Djrill 2.0+ avoids a blanket JSONDateUTCEncoder"""
        # Djrill allows dates for send_at, so shouldn't warn:
        message = mail.EmailMessage('Subject', 'Body', 'from@example.com', ['to@example.com'])
        message.send_at = datetime(2022, 10, 11, 12, 13, 14, 567)
        self.assertNotWarns(DeprecationWarning, message.send)

        # merge_vars need to be json-serializable, so should generate a warning:
        message = mail.EmailMessage('Subject', 'Body', 'from@example.com', ['to@example.com'])
        message.global_merge_vars = {'DATE': date(2022, 10, 11)}
        self.assertWarnsMessage(DeprecationWarning,
                                "Djrill 2.0 will require you to explicitly convert this date to a string",
                                message.send)
        # ... but should still encode the date (for now):
        data = self.get_api_call_data()
        self.assertEqual(data['message']['global_merge_vars'],
                         [{'name': 'DATE', 'content': "2022-10-11 00:00:00"}])

    def assertWarnsMessage(self, warning, message, callable, *args, **kwds):
        """Checks that `callable` issues a warning of category `warning` containing `message`"""
        with warnings.catch_warnings(record=True) as warned:
            warnings.simplefilter("always")
            callable(*args, **kwds)
        self.assertGreater(len(warned), 0, msg="No warnings issued")
        self.assertTrue(
            any(issubclass(w.category, warning) and message in str(w.message) for w in warned),
            msg="%r(%r) not found in %r" % (warning, message, [str(w) for w in warned]))

    def assertNotWarns(self, warning, callable, *args, **kwds):
        """Checks that `callable` does not issue any warnings of category `warning`"""
        with warnings.catch_warnings(record=True) as warned:
            warnings.simplefilter("always")
            callable(*args, **kwds)
        relevant_warnings = [w for w in warned if issubclass(w.category, warning)]
        self.assertEqual(len(relevant_warnings), 0,
                         msg="Unexpected warnings %r" % [str(w) for w in relevant_warnings])


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
