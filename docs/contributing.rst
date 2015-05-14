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

We also have some :ref:`troubleshooting` information that may be helpful.


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

Most of the included tests verify that Djrill constructs the expected Mandrill API
calls, without actually calling Mandrill or sending any email. So these tests
don't require a Mandrill API key, but they *do* require
`mock <http://www.voidspace.org.uk/python/mock/index.html>`_
and `six <https://pythonhosted.org/six/>`_ (``pip install mock six``).

To run the tests, either::

    python -Wall setup.py test

or::

    python -Wall runtests.py


If you set the environment variable `MANDRILL_TEST_API_KEY` to a valid Mandrill
`test API key`_, there are also a handful of integration tests which will run against
the live Mandrill API. (Otherwise these live API tests are skipped.)

.. _test API key: https://mandrill.zendesk.com/hc/en-us/articles/205582447#test_key
