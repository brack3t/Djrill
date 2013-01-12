Djrill, for Mandrill
====================

.. image:: https://secure.travis-ci.org/brack3t/Djrill.png?branch=master
        :target: https://travis-ci.org/brack3t/Djrill

Djrill is an email backend for Django users who want to take advantage of the
Mandrill_ transactional email service from MailChimp_.

In general, Djrill "just works" with Django's built-in `django.core.mail`_
package. You can also take advantage of Mandrill-specific features like tags,
metadata, and tracking.

An optional Django admin interface is included. The admin interface allows you to:

* Check the status of your Mandrill API connection.
* See stats on email senders, tags and urls.

Djrill is made available under the BSD license.

Installation
------------

Install from PyPI::

    pip install djrill

The only dependency other than Django is the requests_ library from Kenneth
Reitz. (If you do not install Djrill using pip or setuptools, you will also
need to ``pip install requests``.)


Configuration
-------------

In ``settings.py``:

1. Add ``djrill`` to your ``INSTALLED_APPS``:

.. code:: python

    INSTALLED_APPS = (
        ...
        "djrill"
    )

2. Add the following line, substituting your own ``MANDRILL_API_KEY``:

.. code:: python

    MANDRILL_API_KEY = "brack3t-is-awesome"

3. Override your existing email backend with the following line:

.. code:: python

    EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

4. (optional) If you want to be able to add senders through Django's admin or
   view stats about your messages, do the following in your base ``urls.py``:

.. code:: python

    ...
    from django.contrib import admin

    from djrill import DjrillAdminSite

    admin.site = DjrillAdminSite()
    admin.autodiscover()
    ...

    urlpatterns = patterns('',
        ...
        url(r'^admin/', include(admin.site.urls)),
    )

Usage
-----

Since you are replacing the global ``EMAIL_BACKEND``, **all** emails are sent
through Mandrill's service. (To selectively use Mandrill for some messages, see
`Using Multiple Email Backends`_ below.)

In general, Djrill "just works" with Django's built-in `django.core.mail`_
package, including ``send_mail``, ``send_mass_mail``, ``EmailMessage`` and
``EmailMultiAlternatives``.

You can also take advantage of Mandrill-specific features like tags, metadata,
and tracking by creating a Django EmailMessage_ (or for HTML,
EmailMultiAlternatives_) object and setting Mandrill-specific
properties on it before calling its ``send`` method. (See
`Mandrill Message Options`_ below.)

Example, sending HTML email with Mandrill tags and metadata:

.. code:: python

    from django.core.mail import EmailMultiAlternatives

    msg = EmailMultiAlternatives(
        subject="Djrill Message",
        body="This is the text version of your email",
        from_email="Djrill Sender <djrill@example.com>",
        to=["Djrill Receiver <djrill.receiver@example.com>", "another.person@example.com"],
        headers={'Reply-To': "Service <support@example.com>"} # optional extra headers
    )
    msg.attach_alternative("<p>This is the HTML version of your email</p>", "text/html")

    # Optional Mandrill-specific extensions (see full list below):
    msg.tags = ["one tag", "two tag", "red tag", "blue tag"]
    msg.metadata = {'user_id': "8675309"}

    # Send it:
    msg.send()

If the email tries to use features that aren't supported by Mandrill, the send
call will raise a ``djrill.NotSupportedByMandrillError`` exception (a subclass
of ValueError).

If the Mandrill API fails or returns an error response, the send call will
raise a ``djrill.MandrillAPIError`` exception (a subclass of
requests.HTTPError).


Django EmailMessage Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Djrill supports most of the functionality of Django's `EmailMessage`_ and
`EmailMultiAlternatives`_ classes. Some notes and limitations:

* **Display Names:** All email addresses (from, to, cc) can be simple
  ("email@example.com") or can include a display name
  ("Real Name <email@example.com>").
* **From Address:** The ``from_email`` must be in one of the approved sending
  domains in your Mandrill account.
* **CC Recipients:** Djrill treats all "cc" recipients as if they were
  additional "to" addresses. (Mandrill does not distinguish "cc" from "to".)
  Note that you will also need to set ``preserve_recipients`` True if you want
  each recipient to see the other recipients listed in the email headers.
* **BCC Recipients:** Mandrill does not permit more than one "bcc" address.
  Djrill raises ``djrill.NotSupportedByMandrillError`` if you attempt to send a
  message with multiple bcc's. (Mandrill's bcc option seems intended primarily
  for logging. To send a single message to multiple recipients without exposing
  their email addresses to each other, simply include them all in the "to" list
  and leave ``preserve_recipients`` set to False.)
* **Attachments:** Djrill includes a message's attachments, but only with the
  mimetypes "text/\*", "image/\*", or "application/pdf" (since that is all
  Mandrill allows). Any other attachment types will raise
  ``djrill.NotSupportedByMandrillError`` when you attempt to send the message.
* **Headers:** Djrill accepts additional headers, but only ``Reply-To`` and
  ``X-*`` (since that is all that Mandrill accepts). Any other extra headers
  will raise ``djrill.NotSupportedByMandrillError`` when you attempt to send the
  message.
* **Alternative Parts:** Djrill requires that if you ``attach_alternative`` to a
  message, there must be only one alternative part, and it must be text/html.
  Otherwise, Djrill will raise ``djrill.NotSupportedByMandrillError`` when you
  attempt to send the message. (Mandrill doesn't support sending multiple html
  alternative parts, or any non-html alternatives.)

Mandrill Message Options
~~~~~~~~~~~~~~~~~~~~~~~~

Many of the options from the Mandrill `messages/send API`_ ``message``
struct can be set directly on an ``EmailMessage`` (or subclass) object:

* ``track_opens`` - Boolean
* ``track_clicks`` - Boolean (If you want to track clicks in HTML only, not
  plaintext mail, you must *not* set this property, and instead just set the
  default in your Mandrill account sending options.)
* ``auto_text`` - Boolean
* ``url_strip_qs`` - Boolean
* ``preserve_recipients`` - Boolean
* ``global_merge_vars`` - a dict -- e.g.,
  ``{ 'company': "ACME", 'offer': "10% off" }``
* ``recipient_merge_vars`` - a dict whose keys are the recipient email addresses
  and whose values are dicts of merge vars for each recipient -- e.g.,
  ``{ 'wiley@example.com': { 'offer': "15% off anvils" } }``
* ``tags`` - a list of strings
* ``google_analytics_domains`` - a list of string domain names
* ``google_analytics_campaign`` - a string or list of strings
* ``metadata`` - a dict
* ``recipient_metadata`` - a dict whose keys are the recipient email addresses,
  and whose values are dicts of metadata for each recipient (similar to
  ``recipient_merge_vars``)

These Mandrill-specific properties work with *any* ``EmailMessage``-derived
object, so you can use them with many other apps that add Django mail
functionality (such as Django template-based messages).

If you have any questions about the python syntax for any of these properties,
see ``DjrillMandrillFeatureTests`` in tests/test_mandrill_send.py for examples.

Mandrill Templates
~~~~~~~~~~~~~~~~~~

To use a Mandrill (MailChimp) template, set a ``template_name`` and (optionally)
``template_content`` on your ``EmailMessage`` object:

.. code:: python

    msg = EmailMessage(subject="Shipped!", from_email="store@example.com",
        to=["customer@example.com", "accounting@example.com"])
    msg.template_name = "SHIPPING_NOTICE"   # A Mandrill template name
    msg.template_content = {                # Content blocks to fill in
        'TRACKING_BLOCK': "<a href='.../\*\|TRACKINGNO\|\*'>track it</a>" }
    msg.global_merge_vars = {               # Merge tags in your template
        'ORDERNO': "12345", 'TRACKINGNO': "1Z987" }
    msg.merge_vars = {                      # Per-recipient merge tags
        'accounting@example.com': { 'NAME': "Pat" },
        'customer@example.com':   { 'NAME': "Kim" } }
    msg.send()

If template_name is set, Djrill will use Mandrill's `messages/send-template API`_,
rather than messages/send. All of the other options listed above can be used.

(This is for *MailChimp* templates stored in your Mandrill account. If you
want to use a *Django* template, you can use Django's render_to_string_ template
shortcut to build the body and html, and send using EmailMultiAlternatives as
in the earlier examples.)

Using Multiple Email Backends
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use Django mail's optional ``connection`` argument to send some mail
through Mandrill and others through a different system. This can be useful to
send customer emails with Mandrill, but admin emails directly through an SMTP
server. Example:

.. code:: python

    from django.core.mail import send_mail, get_connection

    # send_mail connection defaults to the settings EMAIL_BACKEND, which
    # we've set to DjrillBackend. This will be sent using Mandrill:
    send_mail("Subject", "Body", "support@example.com", ["user@example.com"])

    # Get a connection to an SMTP backend, and send using that instead:
    smtp_backend = get_connection('django.core.mail.backends.smtp.EmailBackend')
    send_mail("Subject", "Body", "admin@example.com", ["alert@example.com"],
        connection=smtp_backend)

You can supply a different connection to Django's `django.core.mail`_
``send_mail`` and ``send_mass_mail`` helpers, and in the constructor for an
EmailMessage_ or EmailMultiAlternatives_.


Testing
-------

Djrill is tested against Django 1.3 and 1.4 on Python 2.6 and 2.7, and
Django 1.5RC on Python 2.7 and 3.2.
(It may also work with Django 1.2 and Python 2.5, if you use an older
version of requests compatible with that code.)

.. image:: https://secure.travis-ci.org/brack3t/Djrill.png?branch=master
        :target: https://travis-ci.org/brack3t/Djrill

The included tests verify that Djrill constructs the expected Mandrill API
calls, without actually calling Mandrill or sending any email. So the tests
don't require a Mandrill API key, but they *do* require mock_
(``pip install mock``). To run the tests, either::

    python -Wall setup.py test

or::

    python -Wall runtests.py


Contributing
------------

Djrill is maintained by its users -- it's not managed by the folks at MailChimp.
Pull requests are always welcome to improve support for Mandrill and Django
features.

Please include test cases with pull requests. (And by submitting a pull request,
you're agreeing to release your changes under under the same BSD license as the
rest of this project.)


Release Notes
-------------

Version 0.3.0:

* Attachments are now supported
* Mandrill templates are now supported
* A bcc address is now passed to Mandrill as bcc, rather than being lumped in
  with the "to" recipients. Multiple bcc recipients will now raise an exception,
  as Mandrill only allows one.
* Python 3 support (with Django 1.5)
* Exceptions should be more useful: ``djrill.NotSupportedByMandrillError``
  replaces generic ValueError; ``djrill.MandrillAPIError`` replaces
  DjrillBackendHTTPError, and is now derived from requests.HTTPError. (New
  exceptions are backwards compatible with old ones for existing code.)

Version 0.2.0:

* ``MANDRILL_API_URL`` is no longer required in settings.py
* Earlier versions of Djrill required use of a ``DjrillMessage`` class to
  specify Mandrill-specific options. This is no longer needed -- Mandrill
  options can now be set directly on a Django EmailMessage_ object or any
  subclass. (Existing code can continue to use ``DjrillMessage``.)


Thanks
------

Thanks to the MailChimp team for asking us to build this nifty little app. Also thanks to James Socol on Github for his 
django-adminplus_ library that got us off on the right foot for the custom admin views. Oh, and, of course, Kenneth Reitz for 
the awesome ``requests`` library.


.. _Mandrill: http://mandrill.com
.. _MailChimp: http://mailchimp.com
.. _requests: http://docs.python-requests.org
.. _django-adminplus: https://github.com/jsocol/django-adminplus
.. _mock: http://www.voidspace.org.uk/python/mock/index.html
.. _django.core.mail: https://docs.djangoproject.com/en/dev/topics/email/
.. _EmailMessage: https://docs.djangoproject.com/en/dev/topics/email/#django.core.mail.EmailMessage
.. _EmailMultiAlternatives: https://docs.djangoproject.com/en/dev/topics/email/#sending-alternative-content-types
.. _render_to_string: https://docs.djangoproject.com/en/dev/ref/templates/api/#the-render-to-string-shortcut
.. _messages/send API: https://mandrillapp.com/api/docs/messages.html#method=send
.. _messages/send-template API: https://mandrillapp.com/api/docs/messages.html#method=send-template

