from django.contrib import admin

from djrill.views import (DjrillIndexView, DjrillSendersListView,
                          DjrillTagListView,
                          DjrillUrlListView)

# Only try to register Djrill admin views if DjrillAdminSite
# or django-adminplus is in use
if hasattr(admin.site,'register_view'):
    admin.site.register_view("djrill/senders/", DjrillSendersListView.as_view(),
                             "djrill_senders", "senders")
    admin.site.register_view("djrill/status/", DjrillIndexView.as_view(),
						 	 "djrill_status", "status")
    admin.site.register_view("djrill/tags/", DjrillTagListView.as_view(),
							 "djrill_tags", "tags")
    admin.site.register_view("djrill/urls/", DjrillUrlListView.as_view(),
							 "djrill_urls", "urls")
