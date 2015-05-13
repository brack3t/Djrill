Release Notes
=============

Djrill practices `semantic versioning <semver>`_.
Among other things, this means that minor updates
(1.x to 1.y) should always be backwards-compatible,
and breaking changes will always increment the
major version number (1.x to 2.0).

Upcoming Changes in Djrill 2.0
------------------------------

Djrill 2.0 is under development and will include some breaking changes.
Although the changes won't impact most Djrill users, the current
version of Djrill (1.4) will try to warn you if you use things
that will change. (Warnings appear in the console when running Django
in debug mode.)

* **Djrill Admin site**

  Djrill 2.0 will remove the custom Djrill admin site. It duplicates
  information from Mandrill's dashboard, most Djrill users are unaware
  it exists, and it has caused problems tracking Django admin changes.

  Drill 1.4 will report a `DeprecationWarning` when you try to load
  the `DjrillAdminSite`. You should remove it from your code.

  Also, if you changed :setting:`INSTALLED_APPS` to use
  `'django.contrib.admin.apps.SimpleAdminConfig'`, you may be able to
  switch that back to `'django.contrib.admin'` and let Django
  handle the `admin.autodiscover()` for you.

* **Dates in merge data and other attributes**

  Djrill automatically converts :attr:`send_at` `date` and `datetime`
  values to the ISO 8601 string format expected by the Mandrill API.

  Unintentionally, it also converts dates used in other Mandrill message
  attributes (such as :attr:`merge_vars` or :attr:`metadata`) where it
  might not be expected (or appropriate).

  Djrill 2.0 will remove this automatic date formatting, except
  for attributes that are inherently dates (currently only `send_at`).

  To assist in detecting code relying on the (undocumented) current
  behavior, Djrill 1.4 will report a `DeprecationWarning` for `date`
  or `datetime` values used in any Mandrill message attributes other
  than `send_at`. See :ref:`formatting-merge-data` for other options.

* **DjrillMessage class**

  The ``DjrillMessage`` class has not been needed since Djrill 0.2.
  You can simply set Djrill message attributes on any Django
  :class:`~django.core.mail.EmailMultiAlternatives` object.
  Djrill 1.4 will report a `DeprecationWarning` if you are still
  using ``DjrillMessage``.

* **DjrillBackendHTTPError**

  The ``DjrillBackendHTTPError`` exception was replaced in Djrill 0.3
  with :exc:`djrill.MandrillAPIError`.   Djrill 1.4 will report a
  `DeprecationWarning` if you are still importing ``DjrillBackendHTTPError``.


Change Log
----------

Version 1.4 (development):

* Django 1.8 support
* Support new Django 1.8 EmailMessage reply_to param.
  (Specifying a :ref:`Reply-To header <message-headers>`
  still works, with any version of Django,
  and will override the reply_to param if you use both.)
* More-helpful exception when using a non-JSON-serializable
  type in merge_vars and other Djrill message attributes
* Deprecation warnings for upcoming 2.0 changes (see above)


Version 1.3:

* Use Mandrill secure https API endpoint (rather than http).
* Support :attr:`merge_language` option (for choosing between
  Handlebars and Mailchimp templates).


Version 1.2:

* Support Django 1.7; add testing on Python 3.3, 3.4, and PyPy
* Bug fixes


Version 1.1:

* Allow use of Mandrill template default "from" and "subject" fields,
  via :attr:`use_template_from` and :attr:`use_template_subject`.
* Fix `UnicodeEncodeError` with unicode attachments


Version 1.0:

* Global :setting:`MANDRILL_SUBACCOUNT` setting


Version 0.9:

* Better handling for "cc" and "bcc" recipients.
* Allow all extra message headers in send.
  (Mandrill has relaxed previous API restrictions on headers.)


Version 0.8:

* Expose :ref:`mandrill-response` on sent messages


Version 0.7:

* Support for Mandrill send options :attr:`async`, :attr:`important`,
  :attr:`ip_pool`, :attr:`return_path_domain`, :attr:`send_at`,
  :attr:`subaccount`, and :attr:`view_content_link`


Version 0.6:

* Support for signed webhooks


Version 0.5:

* Support for incoming mail and other Mandrill webhooks
* Support for Mandrill send options :attr:`auto_html`, :attr:`tracking_domain`
  and :attr:`signing_domain`.


Version 0.4:

* Attachments with a Content-ID are now treated as
  :ref:`embedded images <sending-attachments>`
* New Mandrill :attr:`inline_css` option is supported
* Remove limitations on attachment types, to track Mandrill change
* Documentation is now available on
  `djrill.readthedocs.org <https://djrill.readthedocs.org>`_


Version 0.3:

* :ref:`Attachments <sending-attachments>` are now supported
* :ref:`Mandrill templates <mandrill-templates>` are now supported
* A bcc address is now passed to Mandrill as bcc, rather than being lumped in
  with the "to" recipients. Multiple bcc recipients will now raise an exception,
  as Mandrill only allows one.
* Python 3 support (with Django 1.5)
* Exceptions should be more useful:
  :exc:`djrill.NotSupportedByMandrillError` replaces generic ValueError;
  :exc:`djrill.MandrillAPIError` replaces DjrillBackendHTTPError, and is now
  derived from requests.HTTPError.
  (New exceptions are backwards compatible with old ones for existing code.)


Version 0.2:

* ``MANDRILL_API_URL`` is no longer required in settings.py
* Earlier versions of Djrill required use of a ``DjrillMessage`` class to
  specify Mandrill-specific options. This is no longer needed -- Mandrill
  options can now be set directly on a Django ``EmailMessage`` object or any
  subclass. (Existing code can continue to use ``DjrillMessage``.)

.. _semver: http://semver.org
