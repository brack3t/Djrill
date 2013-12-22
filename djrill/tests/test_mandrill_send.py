from base64 import b64decode
from datetime import date, datetime, timedelta, tzinfo
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import os

from django.conf import settings
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import make_msgid

from djrill import MandrillAPIError, NotSupportedByMandrillError
from djrill.mail.backends.djrill import DjrillBackend
from djrill.tests.mock_backend import DjrillBackendMockAPITestCase

def decode_att(att):
    """Returns the original data from base64-encoded attachment content"""
    return b64decode(att.encode('ascii'))


class DjrillBackendTests(DjrillBackendMockAPITestCase):
    """Test Djrill backend support for Django mail wrappers"""

    sample_image_filename = "sample_image.png"

    def sample_image_pathname(self):
        """Returns path to an actual image file in the tests directory"""
        test_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(test_dir, self.sample_image_filename)
        return path

    def sample_image_content(self):
        """Returns contents of an actual image file from the tests directory"""
        filename = self.sample_image_pathname()
        with open(filename, "rb") as f:
            return f.read()

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

    def test_html_only_message(self):
        html_content = '<p>This is an <strong>important</strong> message.</p>'
        email = mail.EmailMessage('Subject', html_content,
            'from@example.com', ['to@example.com'])
        email.content_subtype = "html"  # Main content is now text/html
        email.send()
        self.assert_mandrill_called("/messages/send.json")
        data = self.get_api_call_data()
        self.assertNotIn('text', data['message'])
        self.assertEqual(data['message']['html'], html_content)

    def test_attachments(self):
        email = mail.EmailMessage('Subject', 'Body goes here', 'from@example.com', ['to1@example.com'])

        text_content = "* Item one\n* Item two\n* Item three"
        email.attach(filename="test.txt", content=text_content, mimetype="text/plain")

        # Should guess mimetype if not provided...
        png_content = b"PNG\xb4 pretend this is the contents of a png file"
        email.attach(filename="test.png", content=png_content)

        # Should work with a MIMEBase object (also tests no filename)...
        pdf_content = b"PDF\xb4 pretend this is valid pdf data"
        mimeattachment = MIMEBase('application', 'pdf')
        mimeattachment.set_payload(pdf_content)
        email.attach(mimeattachment)

        # Attachment type that wasn't supported in early Mandrill releases:
        ppt_content = b"PPT\xb4 pretend this is a valid ppt file"
        email.attach(filename="presentation.ppt", content=ppt_content,
                     mimetype="application/vnd.ms-powerpoint")

        email.send()
        data = self.get_api_call_data()
        attachments = data['message']['attachments']
        self.assertEqual(len(attachments), 4)
        self.assertEqual(attachments[0]["type"], "text/plain")
        self.assertEqual(attachments[0]["name"], "test.txt")
        self.assertEqual(decode_att(attachments[0]["content"]).decode('ascii'), text_content)
        self.assertEqual(attachments[1]["type"], "image/png")  # inferred from filename
        self.assertEqual(attachments[1]["name"], "test.png")
        self.assertEqual(decode_att(attachments[1]["content"]), png_content)
        self.assertEqual(attachments[2]["type"], "application/pdf")
        self.assertEqual(attachments[2]["name"], "")  # none
        self.assertEqual(decode_att(attachments[2]["content"]), pdf_content)
        self.assertEqual(attachments[3]["type"], "application/vnd.ms-powerpoint")
        self.assertEqual(attachments[3]["name"], "presentation.ppt")
        self.assertEqual(decode_att(attachments[3]["content"]), ppt_content)
        # Make sure the image attachment is not treated as embedded:
        self.assertFalse('images' in data['message'])

    def test_embedded_images(self):
        image_data = self.sample_image_content()  # Read from a png file
        image_cid = make_msgid("img")  # Content ID per RFC 2045 section 7 (with <...>)
        image_cid_no_brackets = image_cid[1:-1]  # Without <...>, for use as the <img> tag src

        text_content = 'This has an inline image.'
        html_content = '<p>This has an <img src="cid:%s" alt="inline" /> image.</p>' % image_cid_no_brackets
        email = mail.EmailMultiAlternatives('Subject', text_content, 'from@example.com', ['to@example.com'])
        email.attach_alternative(html_content, "text/html")

        image = MIMEImage(image_data)
        image.add_header('Content-ID', image_cid)
        email.attach(image)

        email.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['text'], text_content)
        self.assertEqual(data['message']['html'], html_content)
        self.assertEqual(len(data['message']['images']), 1)
        self.assertEqual(data['message']['images'][0]["type"], "image/png")
        self.assertEqual(data['message']['images'][0]["name"], image_cid)
        self.assertEqual(decode_att(data['message']['images'][0]["content"]), image_data)
        # Make sure neither the html nor the inline image is treated as an attachment:
        self.assertFalse('attachments' in data['message'])

    def test_attached_images(self):
        image_data = self.sample_image_content()

        email = mail.EmailMultiAlternatives('Subject', 'Message', 'from@example.com', ['to@example.com'])
        email.attach_file(self.sample_image_pathname())  # option 1: attach as a file

        image = MIMEImage(image_data)  # option 2: construct the MIMEImage and attach it directly
        email.attach(image)

        email.send()
        data = self.get_api_call_data()
        attachments = data['message']['attachments']
        self.assertEqual(len(attachments), 2)
        self.assertEqual(attachments[0]["type"], "image/png")
        self.assertEqual(attachments[0]["name"], self.sample_image_filename)
        self.assertEqual(decode_att(attachments[0]["content"]), image_data)
        self.assertEqual(attachments[1]["type"], "image/png")
        self.assertEqual(attachments[1]["name"], "")  # unknown -- not attached as file
        self.assertEqual(decode_att(attachments[1]["content"]), image_data)
        # Make sure the image attachments are not treated as embedded:
        self.assertFalse('images' in data['message'])

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
        self.message.important = True
        self.message.auto_text = True
        self.message.auto_html = True
        self.message.inline_css = True
        self.message.preserve_recipients = True
        self.message.view_content_link = False
        self.message.tracking_domain = "click.example.com"
        self.message.signing_domain = "example.com"
        self.message.return_path_domain = "support.example.com"
        self.message.subaccount = "marketing-dept"
        self.message.async = True
        self.message.ip_pool = "Bulk Pool"
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['message']['important'], True)
        self.assertEqual(data['message']['auto_text'], True)
        self.assertEqual(data['message']['auto_html'], True)
        self.assertEqual(data['message']['inline_css'], True)
        self.assertEqual(data['message']['preserve_recipients'], True)
        self.assertEqual(data['message']['view_content_link'], False)
        self.assertEqual(data['message']['tracking_domain'], "click.example.com")
        self.assertEqual(data['message']['signing_domain'], "example.com")
        self.assertEqual(data['message']['return_path_domain'], "support.example.com")
        self.assertEqual(data['message']['subaccount'], "marketing-dept")
        self.assertEqual(data['async'], True)
        self.assertEqual(data['ip_pool'], "Bulk Pool")

    def test_merge(self):
        # Djrill expands simple python dicts into the more-verbose name/content
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
            [ {'name': 'ACCOUNT_TYPE', 'content': "Basic"},
              {'name': "GREETING", 'content': "Hello"} ])
        self.assertEqual(data['message']['merge_vars'],
            [ { 'rcpt': "customer@example.com",
                'vars': [{ 'name': 'ACCOUNT_TYPE', 'content': "Premium" },
                         { 'name': "GREETING", 'content': "Dear Customer"}] },
              { 'rcpt': "guest@example.com",
                'vars': [{ 'name': "GREETING", 'content': "Dear Guest"}] }
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
            # rcpt/values structures the Mandrill API uses
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

    def test_send_at(self):
        # String passed unchanged
        self.message.send_at = "2013-11-12 01:02:03"
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['send_at'], "2013-11-12 01:02:03")

        # Timezone-naive datetime assumed to be UTC
        self.message.send_at = datetime(2022, 10, 11, 12, 13, 14, 567)
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['send_at'], "2022-10-11 12:13:14")

        # Timezone-aware datetime converted to UTC:
        class GMTminus8(tzinfo):
            def utcoffset(self, dt): return timedelta(hours=-8)
            def dst(self, dt): return timedelta(0)

        self.message.send_at = datetime(2016, 3, 4, 5, 6, 7, tzinfo=GMTminus8())
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['send_at'], "2016-03-04 13:06:07")

        # Date-only treated as midnight UTC
        self.message.send_at = date(2022, 10, 22)
        self.message.send()
        data = self.get_api_call_data()
        self.assertEqual(data['send_at'], "2022-10-22 00:00:00")

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
        self.assertFalse('important' in data['message'])
        self.assertFalse('track_opens' in data['message'])
        self.assertFalse('track_clicks' in data['message'])
        self.assertFalse('auto_text' in data['message'])
        self.assertFalse('auto_html' in data['message'])
        self.assertFalse('inline_css' in data['message'])
        self.assertFalse('url_strip_qs' in data['message'])
        self.assertFalse('tags' in data['message'])
        self.assertFalse('preserve_recipients' in data['message'])
        self.assertFalse('view_content_link' in data['message'])
        self.assertFalse('tracking_domain' in data['message'])
        self.assertFalse('signing_domain' in data['message'])
        self.assertFalse('return_path_domain' in data['message'])
        self.assertFalse('subaccount' in data['message'])
        self.assertFalse('google_analytics_domains' in data['message'])
        self.assertFalse('google_analytics_campaign' in data['message'])
        self.assertFalse('metadata' in data['message'])
        self.assertFalse('global_merge_vars' in data['message'])
        self.assertFalse('merge_vars' in data['message'])
        self.assertFalse('recipient_metadata' in data['message'])
        self.assertFalse('images' in data['message'])
        # Options at top level of api params (not in message dict):
        self.assertFalse('send_at' in data)
        self.assertFalse('async' in data)
        self.assertFalse('ip_pool' in data)

    def test_send_attaches_mandrill_response(self):
        """ The mandrill_response should be attached to the message when it is sent """
        response = [{u'status': u'sent', u'_id': u'd2dc8a04fedb463398d2c124fd0f1774',
                          u'email': u'someone@example.com', u'reject_reason': None}]
        self.mock_post.return_value = self.MockResponse(json=response)
        msg = mail.EmailMessage('Subject', 'Message', 'from@example.com', ['to1@example.com'],)
        sent = msg.send()
        self.assertEqual(sent, 1)
        self.assertEqual(msg.mandrill_response, response)

    def test_send_failed_mandrill_response(self):
        """ If the send fails, mandrill_response should be set to None """
        self.mock_post.return_value = self.MockResponse(status_code=500)
        msg = mail.EmailMessage('Subject', 'Message', 'from@example.com', ['to1@example.com'],)
        sent = msg.send(fail_silently=True)
        self.assertEqual(sent, 0)
        self.assertIsNone(msg.mandrill_response)