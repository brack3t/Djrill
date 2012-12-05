from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.utils import simplejson as json

from email.utils import parseaddr
import requests

# This backend was developed against this API endpoint.
# You can override in settings.py, if desired.
MANDRILL_API_URL = "http://mandrillapp.com/api/1.0"

class DjrillBackendHTTPError(Exception):
    """An exception that will turn into an HTTP error response."""
    def __init__(self, status_code, response=None, log_message=None):
        super(DjrillBackendHTTPError, self).__init__()
        self.status_code = status_code
        self.response = response # often contains helpful Mandrill info
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
        self.api_url = getattr(settings, "MANDRILL_API_URL", MANDRILL_API_URL)

        if not self.api_key:
            raise ImproperlyConfigured("You have not set your mandrill api key "
                "in the settings.py file.")

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

        try:
            msg_dict = self._build_standard_message_dict(message)
            self._add_mandrill_options(message, msg_dict)
            if getattr(message, 'alternatives', None):
                self._add_alternatives(message, msg_dict)
        except ValueError:
            if not self.fail_silently:
                raise
            return False

        djrill_it = requests.post(self.api_action, data=json.dumps({
            "key": self.api_key,
            "message": msg_dict
        }))

        if djrill_it.status_code != 200:
            if not self.fail_silently:
                raise DjrillBackendHTTPError(
                    status_code=djrill_it.status_code,
                    response = djrill_it,
                    log_message="Failed to send a message to %s, from %s" %
                                (msg_dict['to'], msg_dict['from_email']))
            return False
        return True

    def _build_standard_message_dict(self, message):
        """Create a Mandrill send message struct from a Django EmailMessage.

        Builds the standard dict that Django's send_mail and send_mass_mail
        use by default. Standard text email messages sent through Django will
        still work through Mandrill.

        Raises ValueError for any standard EmailMessage features that cannot be
        accurately communicated to Mandrill (e.g., prohibited headers).
        """
        sender = sanitize_address(message.from_email, message.encoding)
        from_name, from_email = parseaddr(sender)

        recipients = [parseaddr(sanitize_address(addr, message.encoding))
                      for addr in message.recipients()]
        to_list = [{"email": to_email, "name": to_name}
                   for (to_name, to_email) in recipients]

        msg_dict = {
            "text": message.body,
            "subject": message.subject,
            "from_email": from_email,
            "to": to_list
        }
        if from_name:
            msg_dict["from_name"] = from_name

        if message.extra_headers:
            for k in message.extra_headers.keys():
                if k != "Reply-To" and not k.startswith("X-"):
                    raise ValueError("Invalid message header '%s' - Mandrill "
                                     "only allows Reply-To and X-* headers" % k)
            msg_dict["headers"] = message.extra_headers

        return msg_dict

    def _add_mandrill_options(self, message, msg_dict):
        """Extend msg_dict to include Mandrill options set on message"""
        # Mandrill attributes that can be copied directly:
        mandrill_attrs = [
            'from_name', # overrides display name parsed from from_email above
            'track_opens', 'track_clicks', 'auto_text', 'url_strip_qs',
            'tags', 'preserve_recipients',
            'google_analytics_domains', 'google_analytics_campaign',
            'metadata']
        for attr in mandrill_attrs:
            if hasattr(message, attr):
                msg_dict[attr] = getattr(message, attr)

        # Allow simple python dicts in place of Mandrill
        # [{name:name, value:value},...] arrays...
        if hasattr(message, 'global_merge_vars'):
            msg_dict['global_merge_vars'] = \
                self._expand_merge_vars(message.global_merge_vars)
        if hasattr(message, 'merge_vars'):
            # For testing reproducibility, we sort the recipients
            msg_dict['merge_vars'] = [
                { 'rcpt': rcpt,
                  'vars': self._expand_merge_vars(message.merge_vars[rcpt]) }
                for rcpt in sorted(message.merge_vars.keys())
            ]
        if hasattr(message, 'recipient_metadata'):
            # For testing reproducibility, we sort the recipients
            msg_dict['recipient_metadata'] = [
                { 'rcpt': rcpt, 'values': message.recipient_metadata[rcpt] }
                for rcpt in sorted(message.recipient_metadata.keys())
            ]


    def _expand_merge_vars(self, vars):
        """Convert a Python dict to an array of name-value used by Mandrill.

        { name: value, ... } --> [ {'name': name, 'value': value }, ... ]
        """
        # For testing reproducibility, we sort the keys
        return [ { 'name': name, 'value': vars[name] }
                 for name in sorted(vars.keys()) ]

    def _add_alternatives(self, message, msg_dict):
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

        msg_dict['html'] = content
