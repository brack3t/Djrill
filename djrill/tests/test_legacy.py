# Tests deprecated Djrill features

from datetime import date, datetime
import warnings

from django.core import mail
from django.test import TestCase

from djrill import NotSupportedByMandrillError
from djrill.tests.mock_backend import DjrillBackendMockAPITestCase
from djrill.tests.utils import reset_warning_registry


class DjrillBackendDeprecationTests(DjrillBackendMockAPITestCase):

    def setUp(self):
        reset_warning_registry()
        super(DjrillBackendDeprecationTests, self).setUp()

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


class DjrillLegacyExceptionTests(TestCase):
    def test_NotSupportedByMandrillError(self):
        """Unsupported features used to just raise ValueError in 0.2.0"""
        ex = NotSupportedByMandrillError("testing")
        self.assertIsInstance(ex, ValueError)
