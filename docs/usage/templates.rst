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


.. _formatting-merge-data:

Formatting Merge Data
~~~~~~~~~~~~~~~~~~~~~

If you're using dates, datetimes, Decimals, or anything other than strings and integers,
you'll need to format them into strings for use as merge data::

    product = Product.objects.get(123)  # A Django model
    total_cost = Decimal('19.99')
    ship_date = date(2015, 11, 18)

    # Won't work -- you'll get "not JSON serializable" exceptions:
    msg.global_merge_vars = {
        'PRODUCT': product,
        'TOTAL_COST': total_cost,
        'SHIP_DATE': ship_date
    }

    # Do something this instead:
    msg.global_merge_vars = {
        'PRODUCT': product.name,  # assuming name is a CharField
        'TOTAL_COST': "%.2f" % total_cost,
        'SHIP_DATE': ship_date.strftime('%B %d, %Y')  # US-style "March 15, 2015"
    }

These are just examples. You'll need to determine the best way to format
your merge data as strings.

Although floats are allowed in merge vars, you'll generally want to format them
into strings yourself to avoid surprises with floating-point precision.

Technically, Djrill will accept anything serializable by the Python json package --
which means advanced template users can include dicts and lists as merge vars
(for templates designed to handle objects and arrays).
See the Python :class:`json.JSONEncoder` docs for a list of allowable types.

Djrill will raise :exc:`djrill.NotSerializableForMandrillError` if you attempt
to send a message with non-json-serializable data.


How To Use Default Mandrill Subject and From fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use default Mandrill "subject" or "from" field from your template definition
(overriding your EmailMessage and Django defaults), set the following attrs:
:attr:`use_template_subject` and/or :attr:`use_template_from` on
your :class:`~django.core.mail.EmailMessage` object::

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

