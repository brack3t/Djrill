try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from .views import DjrillWebhookView


urlpatterns = patterns(
    '',

    url(r'^webhook/$', DjrillWebhookView.as_view(), name='djrill_webhook'),
)
