.. Djrill documentation master file, created by
   sphinx-quickstart on Sat Mar  2 13:07:34 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Djrill: Mandrill for Django
===========================

Release |release|

Djrill integrates the `Mandrill <http://mandrill.com>`_ transactional
email service into Django.

In general, Djrill "just works" with Django's built-in
`django.core.mail <https://docs.djangoproject.com/en/dev/topics/email/>`_
functions. It supports:

* HTML email, attachments, extra headers, and other basic email functionality
* Mandrill-specific extensions like tags, metadata, tracking, and MailChimp templates
* An optional Django admin interface

Djrill is tested with Django 1.3 and later (including Python 3 support with Django 1.5).
It is made available under the BSD license.


.. _quickstart:

Quick Start
-----------

1. Install from PyPI:

   .. code-block:: console

    $ pip install djrill


2. Edit your project's :file:`settings.py`:

   .. code-block:: python

    INSTALLED_APPS = (
        ...
        "djrill"
    )

    MANDRILL_API_KEY = "<your Mandrill key>"
    EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"


3. Now the regular `Django email functions <https://docs.djangoproject.com/en/dev/topics/email/>`_
   will send through Mandrill::

    from django.core.mail import send_mail

    send_mail("It works!", "This will get sent through Mandrill",
        "Djrill Sender <djrill@example.com>", ["to@example.com"])


   You could send an HTML message, complete with custom Mandrill tags and metadata::

    from django.core.mail import EmailMultiAlternatives

    msg = EmailMultiAlternatives(
        subject="Djrill Message",
        body="This is the text email body",
        from_email="Djrill Sender <djrill@example.com>",
        to=["Recipient One <someone@example.com>", "another.person@example.com"],
        headers={'Reply-To': "Service <support@example.com>"} # optional extra headers
    )
    msg.attach_alternative("<p>This is the HTML email body</p>", "text/html")

    # Optional Mandrill-specific extensions:
    msg.tags = ["one tag", "two tag", "red tag", "blue tag"]
    msg.metadata = {'user_id': "8675309"}

    # Send it:
    msg.send()

   (Be sure to use a ``from_email`` that's in one of your Mandrill approved sending
   domains, or the message won't get sent.)


Documentation
-------------

.. toctree::
   :maxdepth: 2

   installation
   usage/sending_mail
   usage/templates
   usage/multiple_backends
   contributing
   history


Thanks
------

Thanks to the MailChimp team for asking us to build this nifty little app, and to all of Djrill's
:doc:`contributors <contributing>`. Also thanks to James Socol on Github for his django-adminplus_
library that got us off on the right foot for the custom admin views.
Oh, and, of course, Kenneth Reitz for the awesome requests_ library.

.. _requests: http://docs.python-requests.org
.. _django-adminplus: https://github.com/jsocol/django-adminplus
