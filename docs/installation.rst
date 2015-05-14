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


Mandrill Subaccounts (Optional)
-------------------------------

.. setting:: MANDRILL_SUBACCOUNT

If you are using Mandrill's `subaccounts`_ feature, you can globally set the
subaccount for all messages sent through Djrill::

    MANDRILL_SUBACCOUNT = "client-347"

(You can also set or override the :attr:`subaccount` on each individual message,
with :ref:`Mandrill-specific sending options <mandrill-send-support>`.)

.. versionadded:: 1.0
   MANDRILL_SUBACCOUNT global setting


.. _subaccounts: http://help.mandrill.com/entries/25523278-What-are-subaccounts-
