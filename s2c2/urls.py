from django.conf.urls import patterns, include, url
from django.contrib import admin

from s2c2 import utils
import s2c2.views


urlpatterns = patterns(
    '',
    url(r'^$', s2c2.views.home, name='home'),
    # url(r'^account/', include('account.urls')),
    url(r'^dashboard(?:/(P<uid>\d+))?/$', s2c2.views.dashboard, name='dashboard'),
    url(r'^classroom/(?P<pk>\d+)/$', s2c2.views.classroom, name='classroom'),
    url(r'^center/(?P<pk>\d+)/$', s2c2.views.center, name='center'),
    url(r'^notification/$', s2c2.views.notification, name='notification'),
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^slot/', include('slot.urls', namespace='slot')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^dummy/$', utils.dummy, name='dummy')
)
