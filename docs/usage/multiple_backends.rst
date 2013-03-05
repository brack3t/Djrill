.. _multiple-backends:

Mixing Email Backends
=====================

Since you are replacing Django's global :setting:`EMAIL_BACKEND`, by default
Djrill will handle all outgoing mail, sending everything through Mandrill.

You can use Django mail's optional :func:`connection <django.core.mail.get_connection>`
argument to send some mail through Mandrill and others through a different system.

This could be useful, for example, to deliver customer emails with Mandrill,
but send admin emails directly through an SMTP server:

.. code-block:: python
    :emphasize-lines: 8,10

    from django.core.mail import send_mail, get_connection

    # send_mail connection defaults to the settings EMAIL_BACKEND, which
    # we've set to DjrillBackend. This will be sent using Mandrill:
    send_mail("Thanks", "We sent your order", "sales@example.com", ["customer@example.com"])

    # Get a connection to an SMTP backend, and send using that instead:
    smtp_backend = get_connection('django.core.mail.backends.smtp.EmailBackend')
    send_mail("Uh-Oh", "Need your attention", "admin@example.com", ["alert@example.com"],
        connection=smtp_backend)

You can supply a different connection to Django's
:func:`~django.core.mail.send_mail` and :func:`~django.core.mail.send_mass_mail` helpers,
and in the constructor for an
:class:`~django.core.mail.EmailMessage` or :class:`~django.core.mail.EmailMultiAlternatives`.
