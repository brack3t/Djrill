Djrill, for Mandrill
====================

Djrill is an email backend and new message class for Django users that want to take advantage of the Mandrill transactional email 
service from MailChimp.

Installation
------------

::

    pip install djrill

The only dependency other than Django is the ``requests`` library from Kenneth Reitz. If you do not 
install through PyPI you will need to do ::

    pip install requests

Configuration
-------------

In ``settings.py``:

1. Add ``djrill`` to your ``INSTALLED_APPS``. ::

    INSTALLED_APPS = (
        ...
        "djrill"
    )

2. Add the following two lines, substituting your own ``MANDRILL_API_KEY``::

    MANDRILL_API_KEY = "brack3t-is-awesome"
    MANDRILL_API_URL = "http://mandrillapp.com/api/1.0"

3. Override your existing email backend with the following line::

    EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

4. (optional) If you want to be able to add senders through Django's admin or view stats about your 
   messages, do the following in your base ``urls.py`` ::

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

Coming soon
