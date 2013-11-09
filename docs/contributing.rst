Contributing
============

Djrill is maintained by its users. Your contributions are encouraged!

The `Djrill source code`_ is on github. See `AUTHORS.txt`_ for a list
of some of the people who have helped improve Djrill.

.. _Djrill source code: https://github.com/brack3t/Djrill:
.. _AUTHORS.txt: https://github.com/brack3t/Djrill/blob/master/AUTHORS.txt


Bugs
----

You can report problems or request features in
`Djrill's github issue tracker <https://github.com/brack3t/Djrill/issues>`_.


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

Djrill is `tested on Travis <https://travis-ci.org/brack3t/Djrill>`_ against:

* Django 1.3 on Python 2.6 and 2.7
* Django 1.4 on Python 2.6 and 2.7
* Django 1.5 on Python 2.7 and 3.2
* Django 1.6 on Python 2.7 and 3.2

The included tests verify that Djrill constructs the expected Mandrill API
calls, without actually calling Mandrill or sending any email. So the tests
don't require a Mandrill API key, but they *do* require
`mock <http://www.voidspace.org.uk/python/mock/index.html>`_ (``pip install mock``).

To run the tests, either::

    python -Wall setup.py test

or::

    python -Wall runtests.py

