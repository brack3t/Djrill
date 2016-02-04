.. _webhooks:

Mandrill Webhooks and Inbound Email
===================================

`Mandrill webhooks`_ are used for notification about outbound messages
(bounces, clicks, etc.), and also for delivering inbound email
processed through Mandrill.

Djrill includes optional support for Mandrill's webhook notifications.
If enabled, it will send a Django signal for each event in a webhook.
Your code can connect to this signal for further processing.

.. warning:: Webhook Security

    Webhooks are ordinary urls---they're wide open to the internet.
    You must take steps to secure webhooks, or anyone could submit
    random (or malicious) data to your app simply by invoking your
    webhook URL. For security:

    * Your webhook should only be accessible over SSL (https).
      (This is beyond the scope of Djrill.)

    * Your webhook must include a random, secret key, known only to your
      app and Mandrill. Djrill will verify calls to your webhook, and will
      reject calls without the correct key.

    * You can, optionally include the two settings :setting:`DJRILL_WEBHOOK_SIGNATURE_KEY`
      and :setting:`DJRILL_WEBHOOK_URL` to enforce `webhook signature`_ checking


.. _Mandrill webhooks: http://help.mandrill.com/entries/21738186-Introduction-to-Webhooks
.. _securing webhooks: http://apidocs.mailchimp.com/webhooks/#securing-webhooks
.. _webhook signature: http://help.mandrill.com/entries/23704122-Authenticating-webhook-requests

.. _webhooks-config:

Configuration
-------------

To enable Djrill webhook processing you need to create and set a webhook
secret in your project settings, include the Djrill url routing, and
then add the webhook in the Mandrill control panel.

1. In your project's :file:`settings.py`, add a :setting:`DJRILL_WEBHOOK_SECRET`:

   .. code-block:: python

      DJRILL_WEBHOOK_SECRET = "<create your own random secret>"

   substituting a secret you've generated just for Mandrill webhooks.
   (Do *not* use your Mandrill API key or Django SECRET_KEY for this!)

   An easy way to generate a random secret is to run the command below in a shell:

   .. code-block:: console

      $ python -c "from django.utils import crypto; print crypto.get_random_string(16)"


2. In your base :file:`urls.py`, add routing for the Djrill urls:

   .. code-block:: python

      urlpatterns = patterns('',
          ...
          url(r'^djrill/', include(djrill.urls)),
      )


3. Now you need to tell Mandrill about your webhook:

   * For receiving events on sent messages (e.g., bounces or clickthroughs),
     you'll do this in Mandrill's `webhooks control panel`_.
   * For setting up inbound email through Mandrill, you'll add your webhook
     to Mandrill's `inbound settings`_ under "Routes" for your domain.
   * And if you want both, you'll need to add the webhook in both places.

   In all cases, the "Post to URL" is
   :samp:`{https://yoursite.example.com}/djrill/webhook/?secret={your-secret}`
   substituting your app's own domain, and changing *your-secret* to the secret
   you created in step 1.

   (For sent-message webhooks, don't forget to tick the "Trigger on Events"
   checkboxes for the events you want to receive.)


Once you've completed these steps and your Django app is live on your site,
you can use the Mandrill "Test" commands to verify your webhook configuration.
Then see the next section for setting up Django signal handlers to process
the webhooks.

Incidentally, you have some control over the webhook url.
If you'd like to change the "djrill" prefix, that comes from
the url config in step 2. And if you'd like to change
the *name* of the "secret" query string parameter, you can set
:setting:`DJRILL_WEBHOOK_SECRET_NAME` in your :file:`settings.py`.

For extra security, Mandrill provides a signature in the request header
X-Mandrill-Signature. If you want to verify this signature, you need to provide
the settings :setting:`DJRILL_WEBHOOK_SIGNATURE_KEY` with the webhook-specific
signature key that can be found in the Mandrill admin panel and
:setting:`DJRILL_WEBHOOK_URL` where you should enter the exact URL, including
that you entered in Mandrill when creating the webhook.

.. _webhooks control panel: https://mandrillapp.com/settings/webhooks
.. _inbound settings: https://mandrillapp.com/inbound


.. _webhook-usage:

Webhook Notifications
---------------------

Once you've enabled webhooks, Djrill will send a ``djrill.signals.webhook_event``
custom `Django signal`_ for each Mandrill event it receives.
You can connect your own receiver function to this signal for further processing.

Be sure to read Django's `listening to signals`_ docs for information on defining
and connecting signal receivers.

Examples:

.. code-block:: python

    from djrill.signals import webhook_event
    from django.dispatch import receiver

    @receiver(webhook_event)
    def handle_bounce(sender, event_type, data, **kwargs):
        if event_type == 'hard_bounce' or event_type == 'soft_bounce':
            print "Message to %s bounced: %s" % (
                data['msg']['email'],
                data['msg']['bounce_description']
            )

    @receiver(webhook_event)
    def handle_inbound(sender, event_type, data, **kwargs):
        if event_type == 'inbound':
            print "Inbound message from %s: %s" % (
                data['msg']['from_email'],
                data['msg']['subject']
            )

    @receiver(webhook_event)
    def handle_whitelist_sync(sender, event_type, data, **kwargs):
        if event_type == 'whitelist_add' or event_type == 'whitelist_remove':
            print "Rejection whitelist update: %s email %s (%s)" % (
                data['action'],
                data['reject']['email'],
                data['reject']['reason']
            )


Note that your webhook_event signal handlers will be called for all Mandrill
webhook callbacks, so you should always check the `event_type` param as shown
in the examples above to ensure you're processing the expected events.

Mandrill batches up multiple events into a single webhook call.
Djrill will invoke your signal handler once for each event in the batch.

The available fields in the `data` param are described in Mandrill's documentation:
`sent-message webhooks`_, `inbound webhooks`_, and `whitelist/blacklist sync webooks`_.

.. _Django signal: https://docs.djangoproject.com/en/stable/topics/signals/
.. _inbound webhooks:
    http://help.mandrill.com/entries/22092308-What-is-the-format-of-inbound-email-webhooks-
.. _listening to signals:
    https://docs.djangoproject.com/en/stable/topics/signals/#listening-to-signals
.. _sent-message webhooks: http://help.mandrill.com/entries/21738186-Introduction-to-Webhooks
.. _whitelist/blacklist sync webooks:
    https://mandrill.zendesk.com/hc/en-us/articles/205583297-Sync-Event-Webhook-format
