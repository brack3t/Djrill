from django.contrib import admin

from djrill.views import DjrillIndexView, DjrillSendersListView

admin.site.register_view("djrill/senders/", DjrillSendersListView.as_view(),
    "senders")
admin.site.register_view("djrill/status/", DjrillIndexView.as_view(), "status")
