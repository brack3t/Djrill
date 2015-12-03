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

.. setting:: MANDRILL_API_KEY

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


Also, if you don't already have a :setting:`DEFAULT_FROM_EMAIL` in settings,
this is a good time to add one. (Django's default is "webmaster@localhost",
which won't work with Mandrill.)


Mandrill Webhooks (Optional)
----------------------------

Djrill includes optional support for Mandrill webhooks, including inbound email.
See the Djrill :ref:`webhooks <webhooks>` section for configuration details.


Other Optional Settings
-----------------------

You can optionally add any of these Djrill settings to your :file:`settings.py`.


.. setting:: MANDRILL_IGNORE_RECIPIENT_STATUS

MANDRILL_IGNORE_RECIPIENT_STATUS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set to ``True`` to disable :exc:`djrill.MandrillRecipientsRefused` exceptions
on invalid or rejected recipients. (Default ``False``.)

.. versionadded:: 2.0


.. setting:: MANDRILL_SETTINGS

MANDRILL_SETTINGS
~~~~~~~~~~~~~~~~~

You can supply global default options to apply to all messages sent through Djrill.
Set :setting:`!MANDRILL_SETTINGS` to a dict of these options. Example::

    MANDRILL_SETTINGS = {
        'subaccount': 'client-347',
        'tracking_domain': 'example.com',
        'track_opens': True,
    }

See :ref:`mandrill-send-support` for a list of available options. (Everything
*except* :attr:`merge_vars`, :attr:`recipient_metadata`, and :attr:`send_at`
can be used with :setting:`!MANDRILL_SETTINGS`.)

Attributes set on individual EmailMessage objects will override the global
:setting:`!MANDRILL_SETTINGS` for that message. :attr:`global_merge_vars`
on an EmailMessage will be merged with any ``global_merge_vars`` in
:setting:`!MANDRILL_SETTINGS` (with the ones on the EmailMessage taking
precedence if there are conflicting var names).

.. versionadded:: 2.0


.. setting:: MANDRILL_API_URL

MANDRILL_API_URL
~~~~~~~~~~~~~~~~

The base url for calling the Mandrill API. The default is
``MANDRILL_API_URL = "https://mandrillapp.com/api/1.0"``,
which is the secure, production version of Mandrill's 1.0 API.

(It's unlikely you would need to change this.)


.. setting:: MANDRILL_SUBACCOUNT

MANDRILL_SUBACCOUNT
~~~~~~~~~~~~~~~~~~~

Prior to Djrill 2.0, the :setting:`!MANDRILL_SUBACCOUNT` setting could
be used to globally set the `Mandrill subaccount <subaccounts>`_.
Although this is still supported for compatibility with existing code,
new code should set a global subaccount in :setting:`MANDRILL_SETTINGS`
as shown above.

.. _subaccounts: http://help.mandrill.com/entries/25523278-What-are-subaccounts-
