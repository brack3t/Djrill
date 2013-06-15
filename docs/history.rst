Release Notes
=============

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
