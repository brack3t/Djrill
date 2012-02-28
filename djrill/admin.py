from django.contrib import admin

from djrill.views import (DjrillIndexView, DjrillSendersListView,
                          DjrillDisableSenderView, DjrillVerifySenderView,
                          DjrillAddSenderView, DjrillTagListView,
                          DjrillUrlListView)

admin.site.register_view("djrill/senders/", DjrillSendersListView.as_view(),
    "djrill_senders", "senders")
admin.site.register_view("djrill/status/", DjrillIndexView.as_view(),
    "djrill_status", "status")
admin.site.register_view("djrill/tags/", DjrillTagListView.as_view(),
    "djrill_tags", "tags")
admin.site.register_view("djrill/urls/", DjrillUrlListView.as_view(),
    "djrill_urls", "urls")

admin.site.register_url("djrill/disable/sender/",
    DjrillDisableSenderView.as_view(), "djrill_disable_sender")
admin.site.register_url("djrill/verify/sender/",
    DjrillVerifySenderView.as_view(), "djrill_verify_sender")
admin.site.register_url("djrill/add/sender/",
    DjrillAddSenderView.as_view(), "djrill_add_sender")
