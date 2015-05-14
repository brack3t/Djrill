.. _troubleshooting:

Troubleshooting
===============

Djrill throwing errors? Not sending what you want? Here are some tips...


Figuring Out What's Wrong
-------------------------

* **Check the error message:** Look for a Mandrill error message in your
  web browser or console (running Django in dev mode) or in your server
  error logs. As of v1.4, Djrill reports the detailed Mandrill error when
  something goes wrong. And when the error is something like "invalid API key"
  or "invalid email address", that's probably 90% of what you'll need to know
  to solve the problem.

* **Check the Mandrill API logs:** The Mandrill dashboard includes an
  *incredibly-helpful* list of your `recent API calls`_ -- and you can click
  into each one to see the full request and response. Check to see if the
  data you thought you were sending actually made it into the request, and
  if Mandrill has any complaints in the response.

* **Double-check common issues:**

  * Did you set your :setting:`MANDRILL_API_KEY` in settings.py?
  * Did you add ``'djrill'`` to the list of :setting:`INSTALLED_APPS` in settings.py?
  * Are you using a valid from address? Django's default is "webmaster@localhost",
    which won't cut it. Either specify the ``from_email`` explicitly on every message
    you send through Djrill, or add :setting:`DEFAULT_FROM_EMAIL` to your settings.py.

* **Try it without Djrill:** Try switching your :setting:`EMAIL_BACKEND`
  setting to Django's `File backend`_ and then running your email-sending
  code again. If that causes errors, you'll know the issue is somewhere
  other than Djrill. And you can look through the :setting:`EMAIL_FILE_PATH`
  file contents afterward to see if you're generating the email you want.


.. _recent API calls: https://mandrillapp.com/settings/api
.. _File backend: https://docs.djangoproject.com/en/stable/topics/email/#file-backend


Getting Help
------------

If you've gone through the suggestions above and still aren't sure what's wrong,
the Djrill community is happy to help. Djrill is supported and maintained by the
people who use it -- like you! (We're not Mandrill employees.)

You can ask in either of these places (but please pick only one per question!):

Ask on `StackOverflow`_
  Tag your question with **both** ``Django`` and ``Mandrill`` to get our attention.
  Bonus: a lot of questions about Djrill are actually questions about Django
  itself, so by asking on StackOverflow you'll also get the benefit of the
  thousands of Django experts there.

Open a `GitHub issue`_
  We do our best to answer questions in GitHub issues. And if you've found
  a Djrill bug, that's definitely the place to report it. (Or even fix it --
  see :ref:`contributing`.)

Wherever you ask, it's always helpful to include the relevant portions of your
code, the text of any error messages, and any exception stack traces in your
question.


.. _StackOverflow: http://stackoverflow.com/questions/tagged/django+mandrill
.. _GitHub issue: https://github.com/brack3t/Djrill/issues
