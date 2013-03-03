Installation
============

It's easiest to install Djrill from `PyPI <https://pypi.python.org/pypi/djrill>`_:

    .. code-block:: console

        $ pip install djrill

If you decide to install Djrill some other way, you'll also need to install its
one dependency (other than Django, of course): the `requests <http://docs.python-requests.org>`_
library from Kenneth Reitz.


Configuration
-------------

In your project's :file:`settings.py`:

1. Add :mod:`djrill` to your :setting:`INSTALLED_APPS`::

    INSTALLED_APPS = (
        ...
        "djrill"
    )

2. Add the following line, substituting your own :setting:`MANDRILL_API_KEY`::

    MANDRILL_API_KEY = "brack3t-is-awesome"

3. Override your existing :setting:`EMAIL_BACKEND` with the following line::

    EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"


Admin (Optional)
----------------

Djrill includes an optional Django admin interface, which allows you to:

* Check the status of your Mandrill API connection
* See stats on email senders, tags and urls

If you want to enable the Djrill admin interface, edit your base :file:`urls.py`:

    .. code-block:: python
        :emphasize-lines: 4,6

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
