from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives


class DjrillMessage(EmailMultiAlternatives):
    alternative_subtype = "mandrill"

    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
        connection=None, attachments=None, headers=None, alternatives=None,
        cc=None, from_name=None, tags=None, track_opens=True,
        track_clicks=True):

        super(DjrillMessage, self).__init__(subject, body, from_email, to, bcc,
            connection, attachments, headers, alternatives, cc)

        self.from_name = from_name
        self.tags = self._set_mandrill_tags(tags)
        self.track_opens = track_opens
        self.track_clicks = track_clicks

    def _set_mandrill_tags(self, tags):
        """
        Check that all tags are below 50 chars and that they do not start
        with an underscore.

        Raise ImproperlyConfigured if an underscore tag is passed in to
        alert the user. Any tag over 50 chars is left out of the list.
        """
        tag_list = []

        for tag in tags:
            if len(tag) <= 50 and not tag.startswith("_"):
                tag_list.append(tag)
            elif tag.startswith("_"):
                raise ImproperlyConfigured(
                    "Tags starting with an underscore are reserved for "
                    "internal use and will cause errors with Mandill's API")

        return tag_list
