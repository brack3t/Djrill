Djrill: Mandrill Transactional Email for Django
===============================================

..  This README is reused in multiple places:
    * Github: project page, exactly as it appears here
    * Docs: shared-intro section gets included in docs/index.rst
            quickstart section gets included in docs/quickstart.rst
    * PyPI: project page (via setup.py long_description),
            with several edits to freeze it to the specific PyPI release
            (see long_description_from_readme in setup.py)
    You can use docutils 1.0 markup, but *not* any Sphinx additions.

.. default-role:: literal


.. _shared-intro:

.. This shared-intro section is also included in docs/index.rst

  **PROJECT STATUS: INACTIVE**

  As of April, 2016, Djrill is no longer actively maintained (other
  than security updates). It is likely to keep working unless/until
  Mandrill changes their APIs, but Djrill will not be updated for
  newer Django versions or Mandrill changes.
  (`more info <https://github.com/brack3t/Djrill/issues/111>`_)

  You may be interested in
  `django-anymail <https://github.com/anymail/django-anymail>`_,
  a Djrill fork that supports Mailgun, Postmark, SendGrid, and other
  transactional ESPs (including limited support for Mandrill).


Djrill integrates the `Mandrill <http://mandrill.com>`_ transactional
email service into Django.

In general, Djrill "just works" with Django's built-in `django.core.mail`
package. It includes:

* Support for HTML, attachments, extra headers, and other features of
  `Django's built-in email <https://docs.djangoproject.com/en/stable/topics/email/>`_
* Mandrill-specific extensions like tags, metadata, tracking, and MailChimp templates
* Optional support for Mandrill inbound email and other webhook notifications,
  via Django signals

Djrill is released under the BSD license. It is tested against Django 1.4--1.9
(including Python 3 with Django 1.6+, and PyPy support with Django 1.5+).
Djrill uses `semantic versioning <http://semver.org/>`_.

.. END shared-intro

.. image:: https://travis-ci.org/brack3t/Djrill.png?branch=master
       :target: https://travis-ci.org/brack3t/Djrill
       :alt:    build status on Travis-CI


**Resources**

* Full documentation: https://djrill.readthedocs.org/en/latest/
* Package on PyPI: https://pypi.python.org/pypi/djrill
* Project on Github: https://github.com/brack3t/Djrill


Djrill 1-2-3
------------

.. _quickstart:

.. This quickstart section is also included in docs/quickstart.rst

1. Install Djrill from PyPI:

   .. code-block:: console

        $ pip install djrill


2. Edit your project's ``settings.py``:

   .. code-block:: python

        INSTALLED_APPS = (
            ...
            "djrill"
        )

        MANDRILL_API_KEY = "<your Mandrill key>"
        EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
        DEFAULT_FROM_EMAIL = "you@example.com"  # if you don't already have this in settings


3. Now the regular `Django email functions <https://docs.djangoproject.com/en/stable/topics/email/>`_
   will send through Mandrill:

   .. code-block:: python

        from django.core.mail import send_mail

        send_mail("It works!", "This will get sent through Mandrill",
            "Djrill Sender <djrill@example.com>", ["to@example.com"])


   You could send an HTML message, complete with custom Mandrill tags and metadata:

   .. code-block:: python

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

.. END quickstart


See the `full documentation <https://djrill.readthedocs.org/en/latest/>`_
for more features and options.
