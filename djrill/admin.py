from django.contrib import admin

from djrill.views import DjrillIndexView


admin.site.register_view("djrill", DjrillIndexView.as_view(), "Djrill")
