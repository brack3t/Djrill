Djrill, for Mandrill
====================

.. image:: https://travis-ci.org/brack3t/Djrill.png
        :target: https://secure.travis-ci.org/brack3t/Djrill

Djrill is an email backend and new message class for Django users that want to take advantage of the Mandrill_ transactional
email service from MailChimp_.

An optional Django admin interface is included. The admin interface allows you to:

* Check the status of your Mandrill API connection.
* See stats on email tags and urls.

Djrill is made available under the BSD license.

Installation
------------

::

    pip install djrill

The only dependency other than Django is the requests_ library from Kenneth Reitz. If you do not install through PyPI you will 
need to do ::

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

Since you are replacing the global ``EMAIL_BACKEND``, **all** emails are sent through Mandrill's service.

If you just want to use Mandrill for sending emails through Django's built-in ``send_mail`` and ``send_mass_mail`` methods, all 
you need to do is follow steps 1 through 3 of the above Configuration.

If, however, you want more control over the messages, to include an HTML version, or to attach tags or tracked URLs to an email, 
usage of our ``DjrillMessage`` class, which is a thin wrapper around Django's ``EmailMultiAlternatives`` is required.

Example, in a view: ::

    from django.views.generic import View

    from djrill.mail import DjrillMessage

    class SendEmailView(View):

        def get(self, request):
            subject = "Djrill Message"
            from_email = "djrill@example.com" # this has to be one of your approved senders
            from_name = "Djrill" # optional
            to = ["Djrill Receiver <djrill.receiver@example.com>", "djrill.two@example.com"]
            text_content = "This is the text version of your email"
            html_content = "<p>This is the HTML version of your email</p>" # optional, requires the ``attach_alternative`` line below
            tags = ["one tag", "two tag", "red tag", "blue tag"] # optional, can't be over 50 chars or start with an underscore

            msg = DjrillMessage(subject, text_content, from_email, to, tags=tags, from_name=from_name)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            ... # you'll want to return some sort of HttpResponse

Any tags over 50 characters in length are silently ignored since Mandrill doesn't support them. Any tags starting with an underscore will raise an ``ImproperlyConfigured``
exception. Tags with an underscore are reserved by Mandrill.

If you attach more than one alternative type, an ``ImproperlyConfigured`` exception will be raised. Mandrill does not support attaching 
files to an email, so attachments will be silently ignored.

Not shown above, but settable, are the two options, ``track_clicks`` and ``track_opens``. They are both set to ``True`` by default, but can be set to ``False`` and passed in when you instantiate your ``DjrillMessage`` 
object.

Just like Django's ``EmailMessage`` and ``EmailMultiAlternatives``, ``DjrillMessage`` accepts extra headers through the 
``headers`` argument. Currently it only accepts ``Reply-To`` and ``X-*`` headers since that is all that Mandrill accepts. Any 
extra headers are silently discarded.

Testing
-------

Djrill is tested against Django 1.3 and 1.4 on Python 2.6 and 2.7.
(It may also work with Django 1.2 and Python 2.5, if you use an older
version of requests compatible with that code.)

.. image:: https://travis-ci.org/brack3t/Djrill.png
        :target: https://secure.travis-ci.org/brack3t/Djrill

The included tests verify that Djrill constructs the expected Mandrill API
calls, without actually calling Mandrill or sending any email. So the tests
don't require a Mandrill API key, but they *do* require mock_
(``pip install mock``). To run the tests, either::

    python setup.py test

or::

    python runtests.py


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
