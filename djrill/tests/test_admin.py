import sys

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib import admin

from djrill.tests.mock_backend import DjrillBackendMockAPITestCase


def reset_admin_site():
    """Return the Django admin globals to their original state"""
    admin.site = admin.AdminSite() # restore default
    if 'djrill.admin' in sys.modules:
        del sys.modules['djrill.admin'] # force autodiscover to re-import


class DjrillAdminTests(DjrillBackendMockAPITestCase):
    """Test the Djrill admin site"""

    # These tests currently just verify that the admin site pages load
    # without error -- they don't test any Mandrill-supplied content.
    # (Future improvements could mock the Mandrill responses.)

    # These urls set up the DjrillAdminSite as suggested in the readme
    urls = 'djrill.tests.admin_urls'

    @classmethod
    def setUpClass(cls):
        # Other test cases may muck with the Django admin site globals,
        # so return it to the default state before loading test_admin_urls
        reset_admin_site()

    def setUp(self):
        super(DjrillAdminTests, self).setUp()
        # Must be authenticated staff to access admin site...
        admin = User.objects.create_user('admin', 'admin@example.com', 'secret')
        admin.is_staff = True
        admin.save()
        self.client.login(username='admin', password='secret')

    def test_admin_senders(self):
        response = self.client.get('/admin/djrill/senders/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senders")

    def test_admin_status(self):
        response = self.client.get('/admin/djrill/status/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status")

    def test_admin_tags(self):
        response = self.client.get('/admin/djrill/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tags")

    def test_admin_urls(self):
        response = self.client.get('/admin/djrill/urls/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "URLs")

    def test_admin_index(self):
        """Make sure Djrill section is included in the admin index page"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Djrill")


class DjrillNoAdminTests(TestCase):
    def test_admin_autodiscover_without_djrill(self):
        """Make sure autodiscover doesn't die without DjrillAdminSite"""
        reset_admin_site()
        admin.autodiscover() # test: this shouldn't error
