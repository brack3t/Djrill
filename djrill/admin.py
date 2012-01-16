from django.contrib import admin

from djrill.views import AdminListView


admin.site.register_view("djrill", AdminListView.as_view(), "Djrill")
