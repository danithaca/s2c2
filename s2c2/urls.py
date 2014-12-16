from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^$', 's2c2.views.home', name='home'),
    # url(r'^account/', include('account.urls')),
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^admin/', include(admin.site.urls)),
)
