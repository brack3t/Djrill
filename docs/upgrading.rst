.. _upgrading:

Upgrading from 1.x
==================

Djrill 2.0 includes some breaking changes from 1.x.
These changes should have minimal (or no) impact on most Djrill users,
but if you are upgrading please review the major topics below
to see if they apply to you.

Djrill 1.4 tried to warn you if you were using Djrill features
expected to change in 2.0. If you are seeing any deprecation warnings
with Djrill 1.4, you should fix them before upgrading to 2.0.
(Warnings appear in the console when running Django in debug mode.)

Please see the :ref:`release notes <history>` for a list of new features
and improvements in Djrill 2.0.


Dropped support for Django 1.3, Python 2.6, and Python 3.2
----------------------------------------------------------

Although Djrill may still work with these older configurations,
we no longer test against them. Djrill now requires Django 1.4
or later and Python 2.7, 3.3, or 3.4.

If you require support for these earlier versions, you should
not upgrade to Djrill 2.0. Djrill 1.4 remains available on
pypi, and will continue to receive security fixes.


Removed DjrillAdminSite
-----------------------

Earlier versions of Djrill included a custom Django admin site.
The equivalent functionality is available in Mandrill's dashboard,
and Djrill 2.0 drops support for it.

Although most Djrill users were unaware the admin site existed,
many did follow the earlier versions' instructions to enable it.

If you have added DjrillAdminSite, you will need to remove it for Djrill 2.0.

In your :file:`urls.py`:

    .. code-block:: python

       from djrill import DjrillAdminSite  # REMOVE this
       admin.site = DjrillAdminSite()  # REMOVE this

       admin.autodiscover()  # REMOVE this if you added it only for Djrill

In your :file:`settings.py`:

    .. code-block:: python

       INSTALLED_APPS = (
           ...
           # If you added SimpleAdminConfig only for Djrill:
           'django.contrib.admin.apps.SimpleAdminConfig',  # REMOVE this
           'django.contrib.admin',  # ADD this default back
           ...
       )

(These instructions assume you had changed to SimpleAdminConfig
solely for DjrillAdminSite. If you are using it for custom admin
sites with any other Django apps you use, you should leave it
SimpleAdminConfig in place, but still remove the references to
DjrillAdminSite.)


Added exception for invalid or rejected recipients
--------------------------------------------------

Djrill 2.0 raises a new :exc:`djrill.MandrillRecipientsRefused` exception when
all recipients of a message are invalid or rejected by Mandrill. (This parallels
the behavior of Django's default :setting:`SMTP email backend <EMAIL_BACKEND>`,
which raises :exc:`SMTPRecipientsRefused <smtplib.SMTPRecipientsRefused>` when
all recipients are refused.)

Your email-sending code should handle this exception (along with other
exceptions that could occur during a send). However, if you want to retain the
Djrill 1.x behavior and treat invalid or rejected recipients as successful sends,
you can set :setting:`MANDRILL_IGNORE_RECIPIENT_STATUS` to ``True`` in your settings.py.


Other 2.0 breaking changes
--------------------------

Code that will be affected by these changes is far less common than
for the changes listed above, but they may impact some uses:

Removed unintended date-to-string conversion
  If your code was inadvertently relying on Djrill to automatically
  convert date or datetime values to strings in :attr:`merge_vars`,
  :attr:`metadata`, or other Mandrill message attributes, you must
  now explicitly do the string conversion yourself.
  See :ref:`formatting-merge-data` for an explanation.
  (Djrill 1.4 reported a DeprecationWarning for this case.)

  (This does not affect :attr:`send_at`, where Djrill specifically
  allows date or datetime values.)

Removed DjrillMessage class
  The ``DjrillMessage`` class has not been needed since Djrill 0.2.
  You should replace any uses of it with the standard
  :class:`~django.core.mail.EmailMessage` class.
  (Djrill 1.4 reported a DeprecationWarning for this case.)

Removed DjrillBackendHTTPError
  This exception was deprecated in Djrill 0.3. Replace uses of it
  with :exc:`djrill.MandrillAPIError`.
  (Djrill 1.4 reported a DeprecationWarning for this case.)

Refactored Djrill backend and exceptions
  Several internal details of ``djrill.mail.backends.DjrillBackend``
  and Djrill's exception classes have been significantly updated for 2.0.
  The intent is to make it easier to maintain and extend the backend
  (including creating your own subclasses to override Djrill's default
  behavior). As a result, though, any existing code that depended on
  undocumented Djrill internals may need to be updated.
