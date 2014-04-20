from django.core import mail

from djrill.tests.mock_backend import DjrillBackendMockAPITestCase

from django.conf import settings

class DjrillMandrillSubaccountTests(DjrillBackendMockAPITestCase):
    """Test Djrill backend support for Mandrill subaccounts"""

    def test_send_basic(self):
        mail.send_mail('Subject here', 'Here is the message.',
            'from@example.com', ['to@example.com'], fail_silently=False)
        self.assert_mandrill_called("/messages/send.json")
        data = self.get_api_call_data()
        self.assertEqual(data['message']['subject'], "Subject here")
        self.assertEqual(data['message']['text'], "Here is the message.")
        self.assertFalse('from_name' in data['message'])
        self.assertEqual(data['message']['from_email'], "from@example.com")
        self.assertEqual(len(data['message']['to']), 1)
        self.assertEqual(data['message']['to'][0]['email'], "to@example.com")
        self.assertFalse('subaccount' in data['message'])

    def test_send_from_subaccount(self):
        settings.MANDRILL_SUBACCOUNT = "test_subaccount"
        
        mail.send_mail('Subject here', 'Here is the message.',
            'from@example.com', ['to@example.com'], fail_silently=False)
        self.assert_mandrill_called("/messages/send.json")
        data = self.get_api_call_data()
        self.assertEqual(data['message']['subject'], "Subject here")
        self.assertEqual(data['message']['text'], "Here is the message.")
        self.assertFalse('from_name' in data['message'])
        self.assertEqual(data['message']['from_email'], "from@example.com")
        self.assertEqual(len(data['message']['to']), 1)
        self.assertEqual(data['message']['to'][0]['email'], "to@example.com")
        self.assertEqual(data['message']['subaccount'], settings.MANDRILL_SUBACCOUNT)

    def test_subaccount_message_overrides_setting(self):
        settings.MANDRILL_SUBACCOUNT = "global_setting_subaccount"
        message = mail.EmailMessage(
            'Subject here', 'Here is the message',
            'from@example.com', ['to@example.com'])
        message.subaccount = "individual_message_subaccount"  # should override global setting
        message.send()
        self.assert_mandrill_called("/messages/send.json")
        data = self.get_api_call_data()
        self.assertEqual(data['message']['subaccount'], "individual_message_subaccount")
