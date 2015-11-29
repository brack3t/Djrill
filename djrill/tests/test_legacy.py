# Tests deprecated Djrill features

from django.test import TestCase

from djrill import NotSupportedByMandrillError


class DjrillLegacyExceptionTests(TestCase):
    def test_NotSupportedByMandrillError(self):
        """Unsupported features used to just raise ValueError in 0.2.0"""
        ex = NotSupportedByMandrillError("testing")
        self.assertIsInstance(ex, ValueError)
