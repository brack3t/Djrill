Sending Template Mail
=====================

.. _mandrill-templates:

Mandrill Templates
------------------

.. versionadded:: 0.3
   Mandrill template support

To use a *Mandrill* (MailChimp) template stored in your Mandrill account,
set a :attr:`template_name` and (optionally) :attr:`template_content`
on your :class:`~django.core.mail.EmailMessage` object::

    from django.core.mail import EmailMessage

    msg = EmailMessage(subject="Shipped!", from_email="store@example.com",
                       to=["customer@example.com", "accounting@example.com"])
    msg.template_name = "SHIPPING_NOTICE"           # A Mandrill template name
    msg.template_content = {                        # Content blocks to fill in
        'TRACKING_BLOCK': "<a href='.../*|TRACKINGNO|*'>track it</a>"
    }
    msg.global_merge_vars = {                       # Merge tags in your template
        'ORDERNO': "12345", 'TRACKINGNO': "1Z987"
    }
    msg.merge_vars = {                              # Per-recipient merge tags
        'accounting@example.com': {'NAME': "Pat"},
        'customer@example.com':   {'NAME': "Kim"}
    }
    msg.send()

If :attr:`template_name` is set, Djrill will use Mandrill's
`messages/send-template API <https://mandrillapp.com/api/docs/messages.html#method=send-template>`_,
and will ignore any `body` text set on the `EmailMessage`.

All of Djrill's other :ref:`Mandrill-specific options <mandrill-send-support>`
can be used with templates.

How To Use Default Mandrill Subject and From fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use default Mandrill "subject" or "from" field from your template definition
(overriding your EmailMessage and Django defaults), set the following attrs:
:attr:`use_template_subject` and/or :attr:`use_template_from` on
your :class:`~django.core.mail.EmailMessage` object::
    # ...
    msg.use_template_subject = True
    msg.use_template_from = True
    msg.send()

.. attribute:: use_template_subject

    If `True`, Djrill will omit the subject, and Mandrill will
    use the default subject from the template.

    .. versionadded:: 1.1

.. attribute:: use_template_from

    If `True`, Djrill will omit the "from" field, and Mandrill will
    use the default "from" from the template.

    .. versionadded:: 1.1



.. _django-templates:

Django Templates
----------------

To compose email using *Django* templates, you can use Django's
:func:`~django.template.loaders.django.template.loader.render_to_string`
template shortcut to build the body and html.

Example that builds an email from the templates ``message_subject.txt``,
``message_body.txt`` and ``message_body.html``::

    from django.core.mail import EmailMultiAlternatives
    from django.template import Context
    from django.template.loader import render_to_string

    template_data = {
        'ORDERNO': "12345", 'TRACKINGNO': "1Z987"
    }

    plaintext_context = Context(autoescape=False)  # HTML escaping not appropriate in plaintext
    subject = render_to_string("message_subject.txt", template_data, plaintext_context)
    text_body = render_to_string("message_body.txt", template_data, plaintext_context)
    html_body = render_to_string("message_body.html", template_data)

    msg = EmailMultiAlternatives(subject=subject, from_email="store@example.com",
                                 to=["customer@example.com"], body=text_body)
    msg.attach_alternative(html_body, "text/html")
    msg.send()

