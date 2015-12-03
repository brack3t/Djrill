from django.core import mail
from django.test.utils import override_settings

from .mock_backend import DjrillBackendMockAPITestCase


class DjrillMandrillSubaccountTests(DjrillBackendMockAPITestCase):
    """Test Djrill backend support for Mandrill subaccounts"""

    def test_no_subaccount_by_default(self):
        mail.send_mail('Subject', 'Body', 'from@example.com', ['to@example.com'])
        data = self.get_api_call_data()
        self.assertFalse('subaccount' in data['message'])

    @override_settings(MANDRILL_SETTINGS={'subaccount': 'test_subaccount'})
    def test_subaccount_setting(self):
        mail.send_mail('Subject', 'Body', 'from@example.com', ['to@example.com'])
        data = self.get_api_call_data()
        self.assertEqual(data['message']['subaccount'], "test_subaccount")

    @override_settings(MANDRILL_SETTINGS={'subaccount': 'global_setting_subaccount'})
    def test_subaccount_message_overrides_setting(self):
        message = mail.EmailMessage('Subject', 'Body', 'from@example.com', ['to@example.com'])
        message.subaccount = "individual_message_subaccount"  # should override global setting
        message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['subaccount'], "individual_message_subaccount")

    # Djrill 1.x offered dedicated MANDRILL_SUBACCOUNT setting.
    # In Djrill 2.x, you should use the MANDRILL_SETTINGS dict as in the earlier tests.
    # But we still support the old setting for compatibility:
    @override_settings(MANDRILL_SUBACCOUNT="legacy_setting_subaccount")
    def test_subaccount_legacy_setting(self):
        mail.send_mail('Subject', 'Body', 'from@example.com', ['to@example.com'])
        data = self.get_api_call_data()
        self.assertEqual(data['message']['subaccount'], "legacy_setting_subaccount")

        message = mail.EmailMessage('Subject', 'Body', 'from@example.com', ['to@example.com'])
        message.subaccount = "individual_message_subaccount"  # should override legacy setting
        message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['subaccount'], "individual_message_subaccount")
