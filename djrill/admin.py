from django.contrib import admin

from djrill.views import DjrillIndexView, DjrillSendersListView


admin.site.register_view("djrill", DjrillIndexView.as_view(), "Djrill")
admin.site.register_view("djrill/senders/list", DjrillSendersListView.as_view())
