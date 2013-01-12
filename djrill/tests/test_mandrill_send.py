from base64 import b64encode
from email.mime.base import MIMEBase

from django.conf import settings
from django.core import mail
from django.core.exceptions import ImproperlyConfigured

from djrill import MandrillAPIError, NotSupportedByMandrillError
from djrill.tests.mock_backend import DjrillBackendMockAPITestCase


class DjrillBackendTests(DjrillBackendMockAPITestCase):
    """Test Djrill backend support for Django mail wrappers"""

    def test_send_mail(self):
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

    def test_missing_api_key(self):
        del settings.MANDRILL_API_KEY
        with self.assertRaises(ImproperlyConfigured):
            mail.send_mail('Subject', 'Message', 'from@example.com',
                ['to@example.com'])

    def test_name_addr(self):
        """Make sure RFC2822 name-addr format (with display-name) is allowed

        (Test both sender and recipient addresses)
        """
        msg = mail.EmailMessage('Subject', 'Message',
            'From Name <from@example.com>',
            ['Recipient #1 <to1@example.com>', 'to2@example.com'],
            cc=['Carbon Copy <cc1@example.com>', 'cc2@example.com'],
            bcc=['Blind Copy <bcc@example.com>'])
        msg.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['from_name'], "From Name")
        self.assertEqual(data['message']['from_email'], "from@example.com")
        self.assertEqual(len(data['message']['to']), 4)
        self.assertEqual(data['message']['to'][0]['name'], "Recipient #1")
        self.assertEqual(data['message']['to'][0]['email'], "to1@example.com")
        self.assertEqual(data['message']['to'][1]['name'], "")
        self.assertEqual(data['message']['to'][1]['email'], "to2@example.com")
        self.assertEqual(data['message']['to'][2]['name'], "Carbon Copy")
        self.assertEqual(data['message']['to'][2]['email'], "cc1@example.com")
        self.assertEqual(data['message']['to'][3]['name'], "")
        self.assertEqual(data['message']['to'][3]['email'], "cc2@example.com")
        # Mandrill only supports email, not name, for bcc:
        self.assertEqual(data['message']['bcc_address'], "bcc@example.com")

    def test_email_message(self):
        email = mail.EmailMessage('Subject', 'Body goes here',
            'from@example.com',
            ['to1@example.com', 'Also To <to2@example.com>'],
            bcc=['bcc@example.com'],
            cc=['cc1@example.com', 'Also CC <cc2@example.com>'],
            headers={'Reply-To': 'another@example.com',
                     'X-MyHeader': 'my value'})
        email.send()
        self.assert_mandrill_called("/messages/send.json")
        data = self.get_api_call_data()
        self.assertEqual(data['message']['subject'], "Subject")
        self.assertEqual(data['message']['text'], "Body goes here")
        self.assertEqual(data['message']['from_email'], "from@example.com")
        self.assertEqual(data['message']['headers'],
            { 'Reply-To': 'another@example.com', 'X-MyHeader': 'my value' })
        # Mandrill doesn't have a notion of cc.
        # Djrill just treats cc as additional "to" addresses,
        # which may or may not be what you want.
        self.assertEqual(len(data['message']['to']), 4)
        self.assertEqual(data['message']['to'][0]['email'], "to1@example.com")
        self.assertEqual(data['message']['to'][1]['email'], "to2@example.com")
        self.assertEqual(data['message']['to'][2]['email'], "cc1@example.com")
        self.assertEqual(data['message']['to'][3]['email'], "cc2@example.com")
        self.assertEqual(data['message']['bcc_address'], "bcc@example.com")

    def test_html_message(self):
        text_content = 'This is an important message.'
        html_content = '<p>This is an <strong>important</strong> message.</p>'
        email = mail.EmailMultiAlternatives('Subject', text_content,
            'from@example.com', ['to@example.com'])
        email.attach_alternative(html_content, "text/html")
        email.send()
        self.assert_mandrill_called("/messages/send.json")
        data = self.get_api_call_data()
        self.assertEqual(data['message']['text'], text_content)
        self.assertEqual(data['message']['html'], html_content)
        # Don't accidentally send the html part as an attachment:
        self.assertFalse('attachments' in data['message'])

    def test_attachments(self):
        email = mail.EmailMessage('Subject', 'Body goes here',
            'from@example.com', ['to1@example.com'])

        content1 = "* Item one\n* Item two\n* Item three"
        email.attach(filename="test.txt", content=content1,
            mimetype="text/plain")

        # Should guess mimetype if not provided...
        content2 = "PNG* pretend this is the contents of a png file"
        email.attach(filename="test.png", content=content2)

        # Should work with a MIMEBase object (also tests no filename)...
        content3 = "PDF* pretend this is valid pdf data"
        mimeattachment = MIMEBase('application', 'pdf')
        mimeattachment.set_payload(content3)
        email.attach(mimeattachment)

        email.send()
        data = self.get_api_call_data()
        attachments = data['message']['attachments']
        self.assertEqual(len(attachments), 3)
        self.assertEqual(attachments[0]["type"], "text/plain")
        self.assertEqual(attachments[0]["name"], "test.txt")
        self.assertEqual(attachments[0]["content"], b64encode(content1))
        self.assertEqual(attachments[1]["type"], "image/png") # inferred
        self.assertEqual(attachments[1]["name"], "test.png")
        self.assertEqual(attachments[1]["content"], b64encode(content2))
        self.assertEqual(attachments[2]["type"], "application/pdf")
        self.assertEqual(attachments[2]["name"], "") # none
        self.assertEqual(attachments[2]["content"], b64encode(content3))

    def test_extra_header_errors(self):
        email = mail.EmailMessage('Subject', 'Body', 'from@example.com',
            ['to@example.com'],
            headers={'Non-X-Non-Reply-To-Header': 'not permitted'})
        with self.assertRaises(NotSupportedByMandrillError):
            email.send()

        # Make sure fail_silently is respected
        email = mail.EmailMessage('Subject', 'Body', 'from@example.com',
            ['to@example.com'],
            headers={'Non-X-Non-Reply-To-Header': 'not permitted'})
        sent = email.send(fail_silently=True)
        self.assertFalse(self.mock_post.called,
            msg="Mandrill API should not be called when send fails silently")
        self.assertEqual(sent, 0)

    def test_alternative_errors(self):
        # Multiple alternatives not allowed
        email = mail.EmailMultiAlternatives('Subject', 'Body',
            'from@example.com', ['to@example.com'])
        email.attach_alternative("<p>First html is OK</p>", "text/html")
        email.attach_alternative("<p>But not second html</p>", "text/html")
        with self.assertRaises(NotSupportedByMandrillError):
            email.send()

        # Only html alternatives allowed
        email = mail.EmailMultiAlternatives('Subject', 'Body',
            'from@example.com', ['to@example.com'])
        email.attach_alternative("{'not': 'allowed'}", "application/json")
        with self.assertRaises(NotSupportedByMandrillError):
            email.send()

        # Make sure fail_silently is respected
        email = mail.EmailMultiAlternatives('Subject', 'Body',
            'from@example.com', ['to@example.com'])
        email.attach_alternative("{'not': 'allowed'}", "application/json")
        sent = email.send(fail_silently=True)
        self.assertFalse(self.mock_post.called,
            msg="Mandrill API should not be called when send fails silently")
        self.assertEqual(sent, 0)

    def test_attachment_errors(self):
        # Mandrill silently strips attachments that aren't text/*, image/*,
        # or application/pdf. We want to alert the Djrill user:
        with self.assertRaises(NotSupportedByMandrillError):
            msg = mail.EmailMessage('Subject', 'Body',
                'from@example.com', ['to@example.com'])
            # This is the default mimetype, but won't work with Mandrill:
            msg.attach(content="test", mimetype="application/octet-stream")
            msg.send()

        with self.assertRaises(NotSupportedByMandrillError):
            msg = mail.EmailMessage('Subject', 'Body',
                'from@example.com', ['to@example.com'])
            # Can't send Office docs, either:
            msg.attach(filename="presentation.ppt", content="test",
                mimetype="application/vnd.ms-powerpoint")
            msg.send()

    def test_bcc_errors(self):
        # Mandrill only allows a single bcc address
        with self.assertRaises(NotSupportedByMandrillError):
            msg = mail.EmailMessage('Subject', 'Body',
                'from@example.com', ['to@example.com'],
                bcc=['bcc1@example.com>', 'bcc2@example.com'])
            msg.send()

    def test_mandrill_api_failure(self):
        self.mock_post.return_value = self.MockResponse(status_code=400)
        with self.assertRaises(MandrillAPIError):
            sent = mail.send_mail('Subject', 'Body', 'from@example.com',
                ['to@example.com'])
            self.assertEqual(sent, 0)

        # Make sure fail_silently is respected
        self.mock_post.return_value = self.MockResponse(status_code=400)
        sent = mail.send_mail('Subject', 'Body', 'from@example.com',
            ['to@example.com'], fail_silently=True)
        self.assertEqual(sent, 0)


class DjrillMandrillFeatureTests(DjrillBackendMockAPITestCase):
    """Test Djrill backend support for Mandrill-specific features"""

    def setUp(self):
        super(DjrillMandrillFeatureTests, self).setUp()
        self.message = mail.EmailMessage('Subject', 'Text Body',
            'from@example.com', ['to@example.com'])

    def test_tracking(self):
        # First make sure we're not setting the API param if the track_click
        # attr isn't there. (The Mandrill account option of True for html,
        # False for plaintext can't be communicated through the API, other than
        # by omitting the track_clicks API param to use your account default.)
        self.message.send()
        data = self.get_api_call_data()
        self.assertFalse('track_clicks' in data['message'])
        # Now re-send with the params set
        self.message.track_opens = True
        self.message.track_clicks = True
        self.message.url_strip_qs = True
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['track_opens'], True)
        self.assertEqual(data['message']['track_clicks'], True)
        self.assertEqual(data['message']['url_strip_qs'], True)

    def test_message_options(self):
        self.message.auto_text = True
        self.message.preserve_recipients = True
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['auto_text'], True)
        self.assertEqual(data['message']['preserve_recipients'], True)

    def test_merge(self):
        # Djrill expands simple python dicts into the more-verbose name/value
        # structures the Mandrill API uses
        self.message.global_merge_vars = { 'GREETING': "Hello",
                                           'ACCOUNT_TYPE': "Basic" }
        self.message.merge_vars = {
            "customer@example.com": { 'GREETING': "Dear Customer",
                                      'ACCOUNT_TYPE': "Premium" },
            "guest@example.com": { 'GREETING': "Dear Guest" },
            }
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['global_merge_vars'],
            [ {'name': 'ACCOUNT_TYPE', 'value': "Basic"},
              {'name': "GREETING", 'value': "Hello"} ])
        self.assertEqual(data['message']['merge_vars'],
            [ { 'rcpt': "customer@example.com",
                'vars': [{ 'name': 'ACCOUNT_TYPE', 'value': "Premium" },
                         { 'name': "GREETING", 'value': "Dear Customer"}] },
              { 'rcpt': "guest@example.com",
                'vars': [{ 'name': "GREETING", 'value': "Dear Guest"}] }
            ])

    def test_tags(self):
        self.message.tags = ["receipt", "repeat-user"]
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['tags'], ["receipt", "repeat-user"])

    def test_google_analytics(self):
        self.message.google_analytics_domains = ["example.com"]
        self.message.google_analytics_campaign = "Email Receipts"
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['google_analytics_domains'],
            ["example.com"])
        self.assertEqual(data['message']['google_analytics_campaign'],
            "Email Receipts")

    def test_metadata(self):
        self.message.metadata = { 'batch_num': "12345", 'type': "Receipts" }
        self.message.recipient_metadata = {
            # Djrill expands simple python dicts into the more-verbose
            # name/value structures the Mandrill API uses
            "customer@example.com": { 'cust_id': "67890", 'order_id': "54321" },
            "guest@example.com": { 'cust_id': "94107", 'order_id': "43215" }
        }
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['metadata'], { 'batch_num': "12345",
                                                        'type': "Receipts" })
        self.assertEqual(data['message']['recipient_metadata'],
            [ { 'rcpt': "customer@example.com",
                'values': { 'cust_id': "67890", 'order_id': "54321" } },
              { 'rcpt': "guest@example.com",
                'values': { 'cust_id': "94107", 'order_id': "43215" } }
            ])

    def test_default_omits_options(self):
        """Make sure by default we don't send any Mandrill-specific options.

        Options not specified by the caller should be omitted entirely from
        the Mandrill API call (*not* sent as False or empty). This ensures
        that your Mandrill account settings apply by default.
        """
        self.message.send()
        self.assert_mandrill_called("/messages/send.json")
        data = self.get_api_call_data()
        self.assertFalse('from_name' in data['message'])
        self.assertFalse('bcc_address' in data['message'])
        self.assertFalse('track_opens' in data['message'])
        self.assertFalse('track_clicks' in data['message'])
        self.assertFalse('auto_text' in data['message'])
        self.assertFalse('url_strip_qs' in data['message'])
        self.assertFalse('tags' in data['message'])
        self.assertFalse('preserve_recipients' in data['message'])
        self.assertFalse('google_analytics_domains' in data['message'])
        self.assertFalse('google_analytics_campaign' in data['message'])
        self.assertFalse('metadata' in data['message'])
        self.assertFalse('global_merge_vars' in data['message'])
        self.assertFalse('merge_vars' in data['message'])
        self.assertFalse('recipient_metadata' in data['message'])


