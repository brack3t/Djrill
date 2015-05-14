.. Djrill documentation master file, created by
   sphinx-quickstart on Sat Mar  2 13:07:34 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Djrill: Mandrill Transactional Email for Django
===============================================

Version |release|

.. Incorporate the shared-intro section from the root README:

.. include:: ../README.rst
   :start-after: _shared-intro:
   :end-before:  END shared-intro


Documentation
-------------

.. toctree::
   :maxdepth: 2

   quickstart
   installation
   usage/sending_mail
   usage/templates
   usage/multiple_backends
   usage/webhooks
   troubleshooting
   contributing
   history


Thanks
------

Thanks to the MailChimp team for asking us to build this nifty little app, and to all of Djrill's
:doc:`contributors <contributing>`.
Oh, and, of course, Kenneth Reitz for the awesome requests_ library.

.. _requests: http://docs.python-requests.org
