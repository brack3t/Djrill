from django.core.mail import EmailMultiAlternatives


# DjrillMessage class is deprecated as of 0.2.0, but retained for
# compatibility with existing code. (New code can just set Mandrill-specific
# options directly on an EmailMessage or EmailMultiAlternatives object.)
class DjrillMessage(EmailMultiAlternatives):
    alternative_subtype = "mandrill"

    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
        connection=None, attachments=None, headers=None, alternatives=None,
        cc=None, from_name=None, tags=None, track_opens=True,
        track_clicks=True, preserve_recipients=None):

        super(DjrillMessage, self).__init__(subject, body, from_email, to, bcc,
            connection, attachments, headers, alternatives, cc)

        if from_name:
            self.from_name = from_name
        if tags:
            self.tags = self._set_mandrill_tags(tags)
        if track_opens is not None:
            self.track_opens = track_opens
        if track_clicks is not None:
            self.track_clicks = track_clicks
        if preserve_recipients is not None:
            self.preserve_recipients = preserve_recipients

    def _set_mandrill_tags(self, tags):
        """
        Check that all tags are below 50 chars and that they do not start
        with an underscore.

        Raise ValueError if an underscore tag is passed in to
        alert the user. Any tag over 50 chars is left out of the list.
        """
        tag_list = []

        for tag in tags:
            if len(tag) <= 50 and not tag.startswith("_"):
                tag_list.append(tag)
            elif tag.startswith("_"):
                raise ValueError(
                    "Tags starting with an underscore are reserved for "
                    "internal use and will cause errors with Mandrill's API")

        return tag_list
