Djrill, for Mandrill
====================

Djrill is an email backend and new message class for Django users that want to take advantage of the Mandrill transactional SMTP 
service from MailChimp.

Installation
------------

Coming soon.

Configuration
-------------

In ``settings.py``:

1. Add ``djrill`` to your ``INSTALLED_APPS``.
2. Add the following two lines, substituting your own ``MANDRILL_API_KEY``:

    MANDRILL_API_KEY = "brack3t-is-awesome"
    MANDRILL_API_URL = "http://mandrillapp.com/api/1.0"

3. Override your existing email backend with the following line:

    EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

Usage
-----

Coming soon
