import sys

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib import admin
import six

from djrill.tests.mock_backend import DjrillBackendMockAPITestCase


def reset_admin_site():
    """Return the Django admin globals to their original state"""
    admin.site = admin.AdminSite() # restore default
    if 'djrill.admin' in sys.modules:
        del sys.modules['djrill.admin'] # force autodiscover to re-import


class DjrillAdminTests(DjrillBackendMockAPITestCase):
    """Test the Djrill admin site"""

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
        self.mock_post.return_value = self.MockResponse(raw=self.mock_api_content['users/senders.json'])
        response = self.client.get('/admin/djrill/senders/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senders")
        self.assertContains(response, "sender.example@mandrillapp.com")

    def test_admin_status(self):
        self.mock_post.return_value = self.MockResponse(raw=self.mock_api_content['users/info.json'])
        response = self.client.get('/admin/djrill/status/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status")
        self.assertContains(response, "myusername")

    def test_admin_tags(self):
        self.mock_post.return_value = self.MockResponse(raw=self.mock_api_content['tags/list.json'])
        response = self.client.get('/admin/djrill/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tags")
        self.assertContains(response, "example-tag")

    def test_admin_urls(self):
        self.mock_post.return_value = self.MockResponse(raw=self.mock_api_content['urls/list.json'])
        response = self.client.get('/admin/djrill/urls/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "URLs")
        self.assertContains(response, "example.com/example-page")

    def test_admin_index(self):
        """Make sure Djrill section is included in the admin index page"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Djrill")


    mock_api_content = {
        'users/senders.json': six.b('''
            [
                {
                    "address": "sender.example@mandrillapp.com",
                    "created_at": "2013-01-01 15:30:27",
                    "sent": 42, "hard_bounces": 42, "soft_bounces": 42, "rejects": 42, "complaints": 42,
                    "unsubs": 42, "opens": 42, "clicks": 42, "unique_opens": 42, "unique_clicks": 42
                }
            ]
            '''),

        'users/info.json': six.b('''
            {
                "username": "myusername",
                "created_at": "2013-01-01 15:30:27",
                "public_id": "aaabbbccc112233",
                "reputation": 42,
                "hourly_quota": 42,
                "backlog": 42,
                "stats": {
                    "today": { "sent": 42, "hard_bounces": 42, "soft_bounces": 42, "rejects": 42, "complaints": 42,
                        "unsubs": 42, "opens": 42, "unique_opens": 42, "clicks": 42, "unique_clicks": 42 },
                    "last_7_days": { "sent": 42, "hard_bounces": 42, "soft_bounces": 42, "rejects": 42, "complaints": 42,
                        "unsubs": 42, "opens": 42, "unique_opens": 42, "clicks": 42, "unique_clicks": 42 },
                    "last_30_days": { "sent": 42, "hard_bounces": 42, "soft_bounces": 42, "rejects": 42, "complaints": 42,
                        "unsubs": 42, "opens": 42, "unique_opens": 42, "clicks": 42, "unique_clicks": 42 },
                    "last_60_days": { "sent": 42, "hard_bounces": 42, "soft_bounces": 42, "rejects": 42, "complaints": 42,
                        "unsubs": 42, "opens": 42, "unique_opens": 42, "clicks": 42, "unique_clicks": 42 },
                    "last_90_days": { "sent": 42, "hard_bounces": 42, "soft_bounces": 42, "rejects": 42, "complaints": 42,
                        "unsubs": 42, "opens": 42, "unique_opens": 42, "clicks": 42, "unique_clicks": 42 },
                    "all_time": { "sent": 42, "hard_bounces": 42, "soft_bounces": 42, "rejects": 42, "complaints": 42,
                        "unsubs": 42, "opens": 42, "unique_opens": 42, "clicks": 42, "unique_clicks": 42 }
                }
            }
            '''),

        'tags/list.json': six.b('''
            [
                {
                    "tag": "example-tag",
                    "reputation": 42,
                    "sent": 42, "hard_bounces": 42, "soft_bounces": 42, "rejects": 42, "complaints": 42,
                    "unsubs": 42, "opens": 42, "clicks": 42, "unique_opens": 42, "unique_clicks": 42
                }
            ]
            '''),

        'urls/list.json': six.b('''
            [
                {
                    "url": "http://example.com/example-page",
                    "sent": 42,
                    "clicks": 42,
                    "unique_clicks": 42
                }
            ]
            '''),
    }


class DjrillNoAdminTests(TestCase):
    def test_admin_autodiscover_without_djrill(self):
        """Make sure autodiscover doesn't die without DjrillAdminSite"""
        reset_admin_site()
        admin.autodiscover() # test: this shouldn't error
