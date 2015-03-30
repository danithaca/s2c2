from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib import admin
from p2 import settings, views
from s2c2 import utils


urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^dummy/$', utils.dummy, name='dummy'),

    # note: the following thing about static is only valid in dev.
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)