from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address, DEFAULT_ATTACHMENT_MIME_TYPE

# Oops: this file has the same name as our app, and cannot be renamed.
#from djrill import MANDRILL_API_URL, MandrillAPIError, NotSupportedByMandrillError
from ... import MANDRILL_API_URL, MandrillAPIError, NotSupportedByMandrillError
from ...exceptions import removed_in_djrill_2

from base64 import b64encode
from datetime import date, datetime
from email.mime.base import MIMEBase
from email.utils import parseaddr
import json
import mimetypes
import requests


def encode_date_for_mandrill(dt):
    """Format a date or datetime for use as a Mandrill API date field

    datetime becomes "YYYY-MM-DD HH:MM:SS"
             converted to UTC, if timezone-aware
             microseconds removed
    date     becomes "YYYY-MM-DD 00:00:00"
    anything else gets returned intact
    """
    if isinstance(dt, datetime):
        dt = dt.replace(microsecond=0)
        if dt.utcoffset() is not None:
            dt = (dt - dt.utcoffset()).replace(tzinfo=None)
        return dt.isoformat(' ')
    elif isinstance(dt, date):
        return dt.isoformat() + ' 00:00:00'
    else:
        return dt


class JSONDateUTCEncoder(json.JSONEncoder):
    """[deprecated] JSONEncoder that encodes dates in string format used by Mandrill."""
    def default(self, obj):
        if isinstance(obj, date):
            removed_in_djrill_2(
                "You've used the date '%r' as a Djrill message attribute "
                "(perhaps in merge vars or metadata). Djrill 2.0 will require "
                "you to explicitly convert this date to a string." % obj
            )
            return encode_date_for_mandrill(obj)
        return super(JSONDateUTCEncoder, self).default(obj)


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
        self.api_url = MANDRILL_API_URL

        self.subaccount = getattr(settings, "MANDRILL_SUBACCOUNT", None)

        if not self.api_key:
            raise ImproperlyConfigured("You have not set your mandrill api key "
                "in the settings.py file.")

        self.api_send = self.api_url + "/messages/send.json"
        self.api_send_template = self.api_url + "/messages/send-template.json"

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

        api_url = self.api_send
        api_params = {
            "key": self.api_key,
        }

        try:
            msg_dict = self._build_standard_message_dict(message)
            self._add_mandrill_options(message, msg_dict)
            if getattr(message, 'alternatives', None):
                self._add_alternatives(message, msg_dict)
            self._add_attachments(message, msg_dict)
            api_params['message'] = msg_dict

            # check if template is set in message to send it via
            # api url: /messages/send-template.json
            if hasattr(message, 'template_name'):
                api_url = self.api_send_template
                api_params['template_name'] = message.template_name
                api_params['template_content'] = \
                    self._expand_merge_vars(getattr(message, 'template_content', {}))

            self._add_mandrill_toplevel_options(message, api_params)

        except NotSupportedByMandrillError:
            if not self.fail_silently:
                raise
            return False

        try:
            api_data = json.dumps(api_params, cls=JSONDateUTCEncoder)
        except TypeError as err:
            # Add some context to the "not JSON serializable" message
            if not err.args:
                err.args = ('',)
            err.args = (
                err.args[0] + " in a Djrill message (perhaps it's a merge var?)."
                              " Try converting it to a string or number first.",
            ) + err.args[1:]
            raise err

        response = requests.post(api_url, data=api_data)

        if response.status_code != 200:

            # add a mandrill_response for the sake of being explicit
            message.mandrill_response = None

            if not self.fail_silently:
                log_message = "Failed to send a message"
                if 'to' in msg_dict:
                    log_message += " to " + ','.join(
                        to['email'] for to in msg_dict.get('to', []) if 'email' in to)
                if 'from_email' in msg_dict:
                    log_message += " from %s" % msg_dict['from_email']
                raise MandrillAPIError(
                    status_code=response.status_code,
                    response=response,
                    log_message=log_message)
            return False

        # add the response from mandrill to the EmailMessage so callers can inspect it
        message.mandrill_response = response.json()

        return True

    def _build_standard_message_dict(self, message):
        """Create a Mandrill send message struct from a Django EmailMessage.

        Builds the standard dict that Django's send_mail and send_mass_mail
        use by default. Standard text email messages sent through Django will
        still work through Mandrill.

        Raises NotSupportedByMandrillError for any standard EmailMessage
        features that cannot be accurately communicated to Mandrill.
        """
        sender = sanitize_address(message.from_email, message.encoding)
        from_name, from_email = parseaddr(sender)

        to_list = self._make_mandrill_to_list(message, message.to, "to")
        to_list += self._make_mandrill_to_list(message, message.cc, "cc")
        to_list += self._make_mandrill_to_list(message, message.bcc, "bcc")

        content = "html" if message.content_subtype == "html" else "text"
        msg_dict = {
            content: message.body,
            "to": to_list
        }

        if not getattr(message, 'use_template_from', False):
            msg_dict["from_email"] = from_email
            if from_name:
                msg_dict["from_name"] = from_name

        if not getattr(message, 'use_template_subject', False):
            msg_dict["subject"] = message.subject

        if hasattr(message, 'reply_to'):
            reply_to = [sanitize_address(addr, message.encoding) for addr in message.reply_to]
            msg_dict["headers"] = {'Reply-To': ', '.join(reply_to)}
            # Note: An explicit Reply-To header will override the reply_to attr below
            # (matching Django's own behavior)

        if message.extra_headers:
            msg_dict["headers"] = msg_dict.get("headers", {})
            msg_dict["headers"].update(message.extra_headers)

        return msg_dict

    def _add_mandrill_toplevel_options(self, message, api_params):
        """Extend api_params to include Mandrill global-send options set on message"""
        # Mandrill attributes that can be copied directly:
        mandrill_attrs = [
            'async', 'ip_pool'
        ]
        for attr in mandrill_attrs:
            if hasattr(message, attr):
                api_params[attr] = getattr(message, attr)

        # Mandrill attributes that require conversion:
        if hasattr(message, 'send_at'):
            api_params['send_at'] = encode_date_for_mandrill(message.send_at)


    def _make_mandrill_to_list(self, message, recipients, recipient_type="to"):
        """Create a Mandrill 'to' field from a list of emails.

        Parses "Real Name <address@example.com>" format emails.
        Sanitizes all email addresses.
        """
        parsed_rcpts = [parseaddr(sanitize_address(addr, message.encoding))
                        for addr in recipients]
        return [{"email": to_email, "name": to_name, "type": recipient_type}
                for (to_name, to_email) in parsed_rcpts]

    def _add_mandrill_options(self, message, msg_dict):
        """Extend msg_dict to include Mandrill per-message options set on message"""
        # Mandrill attributes that can be copied directly:
        mandrill_attrs = [
            'from_name', # overrides display name parsed from from_email above
            'important',
            'track_opens', 'track_clicks', 'auto_text', 'auto_html',
            'inline_css', 'url_strip_qs',
            'tracking_domain', 'signing_domain', 'return_path_domain',
            'merge_language',
            'tags', 'preserve_recipients', 'view_content_link', 'subaccount',
            'google_analytics_domains', 'google_analytics_campaign',
            'metadata']

        if self.subaccount:
            msg_dict['subaccount'] = self.subaccount

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

    def _expand_merge_vars(self, vardict):
        """Convert a Python dict to an array of name-content used by Mandrill.

        { name: value, ... } --> [ {'name': name, 'content': value }, ... ]
        """
        # For testing reproducibility, we sort the keys
        return [{'name': name, 'content': vardict[name]}
                for name in sorted(vardict.keys())]

    def _add_alternatives(self, message, msg_dict):
        """
        There can be only one! ... alternative attachment, and it must be text/html.

        Since mandrill does not accept image attachments or anything other
        than HTML, the assumption is the only thing you are attaching is
        the HTML output for your email.
        """
        if len(message.alternatives) > 1:
            raise NotSupportedByMandrillError(
                "Too many alternatives attached to the message. "
                "Mandrill only accepts plain text and html emails.")

        (content, mimetype) = message.alternatives[0]
        if mimetype != 'text/html':
            raise NotSupportedByMandrillError(
                "Invalid alternative mimetype '%s'. "
                "Mandrill only accepts plain text and html emails."
                % mimetype)

        msg_dict['html'] = content

    def _add_attachments(self, message, msg_dict):
        """Extend msg_dict to include any attachments in message"""
        if message.attachments:
            str_encoding = message.encoding or settings.DEFAULT_CHARSET
            mandrill_attachments = []
            mandrill_embedded_images = []
            for attachment in message.attachments:
                att_dict, is_embedded = self._make_mandrill_attachment(attachment, str_encoding)
                if is_embedded:
                    mandrill_embedded_images.append(att_dict)
                else:
                    mandrill_attachments.append(att_dict)
            if len(mandrill_attachments) > 0:
                msg_dict['attachments'] = mandrill_attachments
            if len(mandrill_embedded_images) > 0:
                msg_dict['images'] = mandrill_embedded_images

    def _make_mandrill_attachment(self, attachment, str_encoding=None):
        """Returns EmailMessage.attachments item formatted for sending with Mandrill.

        Returns mandrill_dict, is_embedded_image:
        mandrill_dict: {"type":..., "name":..., "content":...}
        is_embedded_image: True if the attachment should instead be handled as an inline image.

        """
        # Note that an attachment can be either a tuple of (filename, content,
        # mimetype) or a MIMEBase object. (Also, both filename and mimetype may
        # be missing.)
        is_embedded_image = False
        if isinstance(attachment, MIMEBase):
            name = attachment.get_filename()
            content = attachment.get_payload(decode=True)
            mimetype = attachment.get_content_type()
            # Treat image attachments that have content ids as embedded:
            if attachment.get_content_maintype() == "image" and attachment["Content-ID"] is not None:
                is_embedded_image = True
                name = attachment["Content-ID"]
        else:
            (name, content, mimetype) = attachment

        # Guess missing mimetype from filename, borrowed from
        # django.core.mail.EmailMessage._create_attachment()
        if mimetype is None and name is not None:
            mimetype, _ = mimetypes.guess_type(name)
        if mimetype is None:
            mimetype = DEFAULT_ATTACHMENT_MIME_TYPE

        # b64encode requires bytes, so let's convert our content.
        try:
            if isinstance(content, unicode):
                # Python 2.X unicode string
                content = content.encode(str_encoding)
        except NameError:
            # Python 3 doesn't differentiate between strings and unicode
            # Convert python3 unicode str to bytes attachment:
            if isinstance(content, str):
                content = content.encode(str_encoding)

        content_b64 = b64encode(content)

        mandrill_attachment = {
            'type': mimetype,
            'name': name or "",
            'content': content_b64.decode('ascii'),
        }
        return mandrill_attachment, is_embedded_image


############################################################################################
# Recreate this module, but with a warning on attempts to import deprecated properties.
# This is ugly, but (surprisingly) blessed: http://stackoverflow.com/a/7668273/647002
import sys
import types


class ModuleWithDeprecatedProps(types.ModuleType):
    def __init__(self, module):
        self._orig_module = module  # must keep a ref around, or it'll get deallocated
        super(ModuleWithDeprecatedProps, self).__init__(module.__name__, module.__doc__)
        self.__dict__.update(module.__dict__)

    @property
    def DjrillBackendHTTPError(self):
        removed_in_djrill_2("DjrillBackendHTTPError will be removed in Djrill 2.0. "
                            "Use djrill.MandrillAPIError instead.")
        return MandrillAPIError


sys.modules[__name__] = ModuleWithDeprecatedProps(sys.modules[__name__])
