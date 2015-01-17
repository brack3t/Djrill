try:
    from django.conf.urls import include, url
except ImportError:
    # Django 1.3
    from django.conf.urls.defaults import include, url

from django.contrib import admin

from djrill import DjrillAdminSite

# Set up the DjrillAdminSite as suggested in the docs

admin.site = DjrillAdminSite()
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]
