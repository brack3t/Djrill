Sending Mail
============

Djrill handles **all** outgoing email sent through Django's standard
:mod:`django.core.mail` package, including :func:`~django.core.mail.send_mail`,
:func:`~django.core.mail.send_mass_mail`, the :class:`~django.core.mail.EmailMessage` class,
and even :func:`~django.core.mail.mail_admins`.

If you'd like to selectively send only some messages through Mandrill,
there is a way to :ref:`use multiple email backends <multiple-backends>`.


.. _django-send-support:

Django Email Support
--------------------

Djrill supports most of the functionality of Django's :class:`~django.core.mail.EmailMessage`
and :class:`~django.core.mail.EmailMultiAlternatives` classes.

Some notes and limitations:

**Display Names**
    All email addresses (from, to, cc) can be simple
    ("email\@example.com") or can include a display name
    ("Real Name <email\@example.com>").

**From Address**
    The ``from_email`` must be in one of the approved sending
    domains in your Mandrill account, or Mandrill will refuse to send the message.

**CC Recipients**
    Djrill treats all "cc" recipients as if they were
    additional "to" addresses. (Mandrill does not distinguish "cc" from "to".)

    .. note::

        By default, Mandrill hides all recipients from each other. If you want the
        headers to list everyone who was sent the message, you'll also need to set the
        Mandrill option :attr:`preserve_recipients` to `!True`

**BCC Recipients**
    Mandrill does not permit more than one "bcc" address.
    Djrill raises :exc:`~djrill.NotSupportedByMandrillError` if you attempt to send a
    message with multiple bcc's.

    (Mandrill's bcc option seems intended primarily
    for logging. To send a single message to multiple recipients without exposing
    their email addresses to each other, simply include them all in the "to" list
    and leave Mandrill's :attr:`preserve_recipients` set to `!False`.)

    .. versionadded:: 0.3
       Previously "bcc" was treated as "cc"


.. _sending-html:

**HTML/Alternative Parts**
    To include an HTML version of a message, use
    :meth:`~django.core.mail.EmailMultiAlternatives.attach_alternative`:

    .. code-block:: python

        from django.core.mail import EmailMultiAlternatives

        msg = EmailMultiAlternatives("Subject", "text body",
                                     "from@example.com", ["to@example.com"])
        msg.attach_alternative("<html>html body</html>", "text/html")

    Djrill allows a maximum of one
    :meth:`~django.core.mail.EmailMultiAlternatives.attach_alternative`
    on a message, and it must be ``mimetype="text/html"``.
    Otherwise, Djrill will raise :exc:`~djrill.NotSupportedByMandrillError` when you
    attempt to send the message. (Mandrill doesn't support sending multiple html
    alternative parts, or any non-html alternatives.)


.. _sending-attachments:

**Attachments**
    Djrill will send a message's attachments. (Note that Mandrill may impose limits
    on size and type of attachments.)

    Also, if an image attachment has a Content-ID header, Djrill will tell Mandrill
    to treat that as an embedded image rather than an ordinary attachment.
    (For an example, see :meth:`~DjrillBackendTests.test_embedded_images`
    in :file:`tests/test_mandrill_send.py`.)

    .. versionadded:: 0.3
       Attachments

    .. versionchanged:: 0.4
       Special handling for embedded images

**Headers**
    Djrill accepts additional headers, but only ``Reply-To`` and
    ``X-*`` (since that is all that Mandrill accepts). Any other extra headers
    will raise :exc:`~djrill.NotSupportedByMandrillError` when you attempt to send the
    message.


.. _mandrill-send-support:

Mandrill-Specific Options
-------------------------

Most of the options from the Mandrill
`messages/send API <https://mandrillapp.com/api/docs/messages.html#method=send>`_
`message` struct can be set directly on an :class:`~django.core.mail.EmailMessage`
(or subclass) object:

.. These attributes are in the same order as they appear in the Mandrill API docs...

.. attribute:: important

    ``Boolean``: whether Mandrill should send this message ahead of non-important ones.

    .. versionadded:: 0.7

.. attribute:: track_opens

    ``Boolean``: whether Mandrill should enable open-tracking for this message.
    Default from your Mandrill account settings. ::

        message.track_opens = True

.. attribute:: track_clicks

    ``Boolean``: whether Mandrill should enable click-tracking for this message.
    Default from your Mandrill account settings.

    .. note::

        Mandrill has an option to track clicks in HTML email but not plaintext, but
        it's *only* available in your Mandrill account settings. If you want to use that
        option, set it at Mandrill, and *don't* set the ``track_clicks`` attribute here.

.. attribute:: auto_text

    ``Boolean``: whether Mandrill should automatically generate a text body from the HTML.
    Default from your Mandrill account settings.

.. attribute:: auto_html

    ``Boolean``: whether Mandrill should automatically generate an HTML body from the plaintext.
    Default from your Mandrill account settings.

.. attribute:: inline_css

    ``Boolean``: whether Mandrill should inline CSS styles in the HTML.
    Default from your Mandrill account settings.

    .. versionadded:: 0.4

.. attribute:: url_strip_qs

    ``Boolean``: whether Mandrill should ignore any query parameters when aggregating
    URL tracking data. Default from your Mandrill account settings.

.. attribute:: preserve_recipients

    ``Boolean``: whether Mandrill should include all recipients in the "to" message header.
    Default from your Mandrill account settings.

.. attribute:: view_content_link

    ``Boolean``: set False on sensitive messages to instruct Mandrill not to log the content.

    .. versionadded:: 0.7

.. attribute:: tracking_domain

    ``str``: domain Mandrill should use to rewrite tracked links and host tracking pixels
    for this message. Useful if you send email from multiple domains.
    Default from your Mandrill account settings.

.. attribute:: signing_domain

    ``str``: domain Mandrill should use for DKIM signing and SPF on this message.
    Useful if you send email from multiple domains.
    Default from your Mandrill account settings.

.. attribute:: return_path_domain

    ``str``: domain Mandrill should use for the message's return-path.

    .. versionadded:: 0.7

.. attribute:: global_merge_vars

    ``dict``: merge variables to use for all recipients (most useful with :ref:`mandrill-templates`). ::

        message.global_merge_vars = {'company': "ACME", 'offer': "10% off"}

.. attribute:: merge_vars

    ``dict``: per-recipient merge variables (most useful with :ref:`mandrill-templates`). The keys
    in the dict are the recipient email addresses, and the values are dicts of merge vars for
    each recipient::

        message.merge_vars = {
            'wiley@example.com': {'offer': "15% off anvils"},
            'rr@example.com':    {'offer': "instant tunnel paint"}
        }

.. attribute:: tags

    ``list`` of ``str``: tags to apply to the message, for filtering reports in the Mandrill
    dashboard. (Note that Mandrill prohibits tags longer than 50 characters or starting with
    underscores.) ::

        message.tags = ["Order Confirmation", "Test Variant A"]

.. attribute:: subaccount

    ``str``: the ID of one of your subaccounts to use for sending this message.

    .. versionadded:: 0.7

.. attribute:: google_analytics_domains

    ``list`` of ``str``: domain names for links where Mandrill should add Google Analytics
    tracking parameters. ::

        message.google_analytics_domains = ["example.com"]

.. attribute:: google_analytics_campaign

    ``str`` or ``list`` of ``str``: the utm_campaign tracking parameter to attach to links
    when adding Google Analytics tracking. (Mandrill defaults to the message's from_email as
    the campaign name.)

.. attribute:: metadata

    ``dict``: metadata values Mandrill should store with the message for later search and
    retrieval. ::

        message.metadata = {'customer': customer.id, 'order': order.reference_number}

.. attribute:: recipient_metadata

    ``dict``: per-recipient metadata values. Keys are the recipient email addresses,
    and values are dicts of metadata for each recipient (similar to
    :attr:`merge_vars`)

.. attribute:: async

    ``Boolean``: whether Mandrill should use an async mode optimized for bulk sending.

    .. versionadded:: 0.7

.. attribute:: ip_pool

    ``str``: name of one of your Mandrill dedicated IP pools to use for sending this message.

    .. versionadded:: 0.7

.. attribute:: send_at

    ``datetime`` or ``date`` or ``str``: instructs Mandrill to delay sending this message
    until the specified time. (Djrill allows timezone-aware Python datetimes, and converts them
    to UTC for Mandrill. Timezone-naive datetimes are assumed to be UTC.)

    .. versionadded:: 0.7


These Mandrill-specific properties work with *any*
:class:`~django.core.mail.EmailMessage`-derived object, so you can use them with
many other apps that add Django mail functionality.

If you have questions about the python syntax for any of these properties,
see :class:`DjrillMandrillFeatureTests` in :file:`tests/test_mandrill_send.py` for examples.


.. _djrill-exceptions:

Exceptions
----------

.. versionadded:: 0.3
   Djrill-specific exceptions

.. exception:: djrill.NotSupportedByMandrillError

    If the email tries to use features that aren't supported by Mandrill, the send
    call will raise a :exc:`~!djrill.NotSupportedByMandrillError` exception (a subclass
    of :exc:`ValueError`).


.. exception:: djrill.MandrillAPIError

    If the Mandrill API fails or returns an error response, the send call will
    raise a :exc:`~!djrill.MandrillAPIError` exception (a subclass of :exc:`requests.HTTPError`).
    The exception's :attr:`status_code` and :attr:`response` attributes may
    help explain what went wrong.
