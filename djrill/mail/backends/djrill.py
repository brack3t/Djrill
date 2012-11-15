from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.utils import simplejson as json

from email.utils import parseaddr
import requests

class DjrillBackendHTTPError(Exception):
    """An exception that will turn into an HTTP error response."""
    def __init__(self, status_code, log_message=None):
        super(DjrillBackendHTTPError, self).__init__()
        self.status_code = status_code
        self.log_message = log_message

    def __str__(self):
        message = "DjrillBackendHTTP %d" % self.status_code
        if self.log_message:
            return message + " " + self.log_message
        else:
            return message


class DjrillBackend(BaseEmailBackend):
    """
    Mandrill API Email Backend
    """

    def __init__(self, **kwargs):
        """
        Set the API key, API url and set the action url.
        """
        super(DjrillBackend, self).__init__(**kwargs)
        self.api_key = getattr(settings, "MANDRILL_API_KEY", None)
        self.api_url = getattr(settings, "MANDRILL_API_URL", None)

        if not self.api_key:
            raise ImproperlyConfigured("You have not set your mandrill api key "
                "in the settings.py file.")
        if not self.api_url:
            raise ImproperlyConfigured("You have not added the Mandrill api "
                "url to your settings.py")

        self.api_action = self.api_url + "/messages/send.json"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        num_sent = 0
        for message in email_messages:
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
        self.recipients = [{"email": e, "name": n} for n,e in [
            parseaddr(r) for r in recipients_list]]

        self.msg_dict = self._build_standard_message_dict(message)

        if getattr(message, "alternative_subtype", None):
            if message.alternative_subtype == "mandrill":
                self._build_advanced_message_dict(message)
        try:
            if getattr(message, 'alternatives', None):
                self._add_alternatives(message)
        except ValueError:
            if not self.fail_silently:
                raise
            return False

        djrill_it = requests.post(self.api_action, data=json.dumps({
            "key": self.api_key,
            "message": self.msg_dict
        }))

        if djrill_it.status_code != 200:
            if not self.fail_silently:
                raise DjrillBackendHTTPError(
                    status_code=djrill_it.status_code,
                    log_message="Failed to send a message to %s, from %s" %
                                (self.recipients, self.sender))
            return False
        return True

    def _build_standard_message_dict(self, message):
        """
        Build standard message dict.

        Builds the standard dict that Django's send_mail and send_mass_mail
        use by default. Standard text email messages sent through Django will
        still work through Mandrill.
        """
        from_name, from_email = parseaddr(self.sender)
        msg_dict = {
            "text": message.body,
            "subject": message.subject,
            "from_email": from_email,
            "to": self.recipients
        }
        if from_name:
            msg_dict["from_name"] = from_name

        if message.extra_headers:
            accepted_headers = {}
            for k in message.extra_headers.keys():
                if k.startswith("X-") or k == "Reply-To":
                    accepted_headers.update(
                        {"%s" % k: message.extra_headers[k]})
            msg_dict.update({"headers": accepted_headers})

        return msg_dict

    def _build_advanced_message_dict(self, message):
        """
        Builds advanced message dict
        """
        self.msg_dict.update({
            "tags": message.tags,
            "track_opens": message.track_opens,
            "track_clicks": message.track_clicks
        })
        if message.from_name:
            self.msg_dict["from_name"] = message.from_name


    def _add_alternatives(self, message):
        """
        There can be only one! ... alternative attachment, and it must be text/html.

        Since mandrill does not accept image attachments or anything other
        than HTML, the assumption is the only thing you are attaching is
        the HTML output for your email.
        """
        if len(message.alternatives) > 1:
            raise ValueError(
                "Too many alternatives attached to the message. "
                "Mandrill only accepts plain text and html emails.")

        (content, mimetype) = message.alternatives[0]
        if mimetype != 'text/html':
            raise ValueError("Invalid alternative mimetype '%s'. "
                             "Mandrill only accepts plain text and html emails."
                             % mimetype)

        self.msg_dict.update({
            "html": content
        })
