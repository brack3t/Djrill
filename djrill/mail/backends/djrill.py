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

        sender = sanitize_address(message.from_email, message.encoding)
        recipients = [{"email": sanitize_address(addr, message.encoding)}
            for addr in message.recipients()]

        djrill_it = requests.post(self.api_action, data=json.dumps({
            "key": self.api_key,
            "message": {
                "html": message.body,
                "text": message.body,
                "subject": message.subject,
                "from_email": sender,
                "from_name": "Devs",
                "to": recipients
            }
        }))

        if djrill_it.status_code != 200:
            if not self.fail_silently:
                raise
            return False
        return True
