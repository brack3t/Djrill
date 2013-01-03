try:
    from django.conf.urls import include, patterns, url
except ImportError:
    # Django 1.3
    from django.conf.urls.defaults import include, patterns, url

from django.contrib import admin

from djrill import DjrillAdminSite

admin.site = DjrillAdminSite()
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
