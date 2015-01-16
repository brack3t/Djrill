Contributing
============

Djrill is maintained by its users. Your contributions are encouraged!

The `Djrill source code`_ is on github. See `AUTHORS.txt`_ for a list
of some of the people who have helped improve Djrill.

.. _Djrill source code: https://github.com/brack3t/Djrill
.. _AUTHORS.txt: https://github.com/brack3t/Djrill/blob/master/AUTHORS.txt


Bugs
----

You can report problems or request features in
`Djrill's github issue tracker <https://github.com/brack3t/Djrill/issues>`_.

(If you're seeing a :exc:`djrill.MandrillAPIError`, chances are good you're asking
Djrill to tell Mandrill to do something it doesn't want to. Mandrill keeps a
really-helpful `API error log <https://mandrillapp.com/settings/api>`_ which will
often help you figure out what went wrong.)


Pull Requests
-------------

Pull requests are always welcome to fix bugs and improve support for Mandrill and Django features.

* Please include test cases.
* We try to follow the `Django coding style`_ (basically, PEP 8 with longer lines OK).
* By submitting a pull request, you're agreeing to release your changes under under
  the same BSD license as the rest of this project.

.. _Django coding style: https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/


Testing
-------

Djrill is `tested on Travis <https://travis-ci.org/brack3t/Djrill>`_ against several
combinations of Django and Python versions. (Full list in
`.travis.yml <https://github.com/brack3t/Djrill/blob/master/.travis.yml>`_.)

The included tests verify that Djrill constructs the expected Mandrill API
calls, without actually calling Mandrill or sending any email. So the tests
don't require a Mandrill API key, but they *do* require
`mock <http://www.voidspace.org.uk/python/mock/index.html>`_
and `six <https://pythonhosted.org/six/>`_ (``pip install mock six``).

To run the tests, either::

    python -Wall setup.py test

or::

    python -Wall runtests.py

