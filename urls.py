from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

from djrill import DjrillAdminSite

admin.site = DjrillAdminSite()
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'djrill.views.home', name='home'),
    # url(r'^djrill/', include('djrill.foo.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
