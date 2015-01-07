from django.conf.urls import patterns, include, url
from django.contrib import admin
import s2c2.views

urlpatterns = patterns(
    '',
    url(r'^$', s2c2.views.home, name='home'),
    # url(r'^account/', include('account.urls')),
    url(r'^dashboard(?:/(P<uid>\d+))?/$', s2c2.views.dashboard, name='dashboard'),
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^admin/', include(admin.site.urls)),
)
