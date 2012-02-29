Djrill, for Mandrill
====================

Djrill is an email backend and new message class for Django users that want to take advantage of the Mandrill transactional email 
service from MailChimp.

An optional Django admin interface is included. The admin interface allows you to: check the status of your Mandrill API connection

* Check the status of your Mandrill API connection.
* Add/disable email senders.
* See stats on email tags and urls.

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

If you just want to use Mandrill for sending emails through Django's built-in ``send_mail`` and ``send_mass_mail`` methods, all 
you need to do is follow steps 1 through 3 of the above Configuration. If, however, you want more control over the messages, to 
include an HTML version, or to attach tags to an email, a little more work is required.

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
            html_content = "<p>This is the HTML version of your email</p> # optional, requires the ``attach_alternative`` line below
            tags = ["one tag", "two tag", "red tag", "blue tag"] # optional, can't be over 50 chars or start with an underscore

            msg = DjrillMessage(subject, text_content, from_email, to, tags=tags, from_name=from_name)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
