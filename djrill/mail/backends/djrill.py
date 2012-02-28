from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.utils import simplejson as json

import requests


class DjrillBackend(BaseEmailBackend):
    """
    Mandrill API Email Backend
    """

    def __init__(self, fail_silently=False, **kwargs):
        """
        Set the API key, API url and set the action url.
        """
        super(DjrillBackend, self).__init__(**kwargs)
        self.api_key = getattr(settings, "MANDRILL_API_KEY", None)
        self.api_url = getattr(settings, "MANDRILL_API_URL", None)
        self.connection = None

        if not self.api_key:
            raise ImproperlyConfigured("You have not set your mandrill api key "
                "in the settings.py file.")
        if not self.api_url:
            raise ImproperlyConfigured("You have not added the Mandrill api "
                "url to your settings.py")

        self.api_action = self.api_url + "/messages/send.json"
        self.api_verify = self.api_url + "/users/verify-sender.json"

    def open(self, sender):
        """
        """
        self.connection = None

        valid_sender = requests.post(
            self.api_verify, data={"key": self.api_key, "email": sender})

        if valid_sender.status_code == 200:
            data = json.loads(valid_sender.content)
            if data["is_enabled"]:
                self.connection = True
                return True
        else:
            if not self.fail_silently:
                raise

    def send_messages(self, email_messages):
        if not email_messages:
            return

        num_sent = 0
        for message in email_messages:
            self.open(message.from_email)
            if not self.connection:
                return

            sent = self._send(message)

            if sent:
                num_sent += 1

        return num_sent

    def _send(self, message):
        if not message.recipients():
            return False

        self.sender = sanitize_address(message.from_email, message.encoding)
        recipients_list = [sanitize_address(addr, message.encoding)
            for addr in message.recipients()]
        from email.utils import parseaddr
        self.recipients = [{"email": e, "name": n} for n,e in [
            parseaddr(r) for r in recipients_list]]

        self.msg_dict = self._build_standard_message_dict(message)

        if getattr(message, "alternative_subtype", None):
            if message.alternative_subtype == "mandrill":
                self._build_advanced_message_dict(message)
                if message.alternatives:
                    self._add_alternatives(message)

        djrill_it = requests.post(self.api_action, data=json.dumps({
            "key": self.api_key,
            "message": self.msg_dict
        }))

        if djrill_it.status_code != 200:
            if not self.fail_silently:
                raise
            return False
        return True

    def _build_standard_message_dict(self, message):
        """
        Build standard message dict.

        Builds the standard dict that Django's send_mail and send_mass_mail
        use by default. Standard text email messages sent through Django will
        still work through Mandrill.
        """
        return {
            "text": message.body,
            "subject": message.subject,
            "from_email": self.sender,
            "to": self.recipients
        }

    def _build_advanced_message_dict(self, message):
        """
        Builds advanced message dict and attaches any accepted extra headers.
        """
        self.msg_dict.update({
            "from_name": message.from_name,
            "tags": message.tags,
            "track_opens": message.track_opens,
        })

        if message.extra_headers:
            accepted_headers = {}

            for k in message.extra_headers.keys():
                if k.startswith("X-") or k == "Reply-To":
                    accepted_headers.update(
                        {"%s" % k: message.extra_headers[k]})
            self.msg_dict.update({"headers": accepted_headers})

    def _add_alternatives(self, message):
        """
        There can be only one! ... alternative attachment.

        Since mandrill does not accept image attachments or anything other
        than HTML, the assumption is the only thing you are attaching is
        the HTML output for your email.
        """
        if len(message.alternatives) > 1:
            raise ImproperlyConfigured(
                "Mandrill only accepts plain text and html emails. Please "
                "check the alternatives you have attached to your message.")

        self.msg_dict.update({
            "html": message.alternatives[0][0],
            "track_clicks": message.track_clicks
        })
