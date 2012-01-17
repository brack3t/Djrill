from django.contrib import admin

from djrill.views import (DjrillIndexView, DjrillSendersListView,
                            DjrillDisableSenderView, DjrillVerifySenderView)

admin.site.register_view("djrill/senders/", DjrillSendersListView.as_view(),
    "djrill_sender", "senders")
admin.site.register_view("djrill/status/", DjrillIndexView.as_view(),
    "djrill_status", "status")

admin.site.register_url("djrill/disable/sender/",
    DjrillDisableSenderView.as_view(), "djrill_disable_sender")
admin.site.register_url("djrill/verify/sender/",
    DjrillVerifySenderView.as_view(), "djrill_verify_sender")
