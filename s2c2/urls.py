from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static

from s2c2 import utils
import s2c2.views
from . import settings


urlpatterns = patterns(
    '',
    url(r'^$', s2c2.views.home, name='home'),
    # url(r'^account/', include('account.urls')),
    url(r'^dashboard(?:/(?P<uid>\d+))?/$', s2c2.views.dashboard, name='dashboard'),
    url(r'^classroom/(?P<pk>\d+)/$', s2c2.views.classroom_home, name='classroom'),

    url(r'^center/(?P<pk>\d+)/$', s2c2.views.center_home, name='center'),
    url(r'^center/(?P<pk>\d+)/directory/$', s2c2.views.center_home, {'tab': 'directory'}, name='center_directory'),
    url(r'^center/(?P<pk>\d+)/list-classroom/$', s2c2.views.center_home, {'tab': 'list-classroom'}, name='center_list_classroom'),
    url(r'^center/(?P<pk>\d+)/list-staff/$', s2c2.views.center_home, {'tab': 'list-staff'}, name='center_list_staff'),

    url(r'^notification/$', s2c2.views.notification, name='notification'),

    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^slot/', include('slot.urls', namespace='slot')),
    url(r'^log/', include('log.urls', namespace='log')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^dummy/$', utils.dummy, name='dummy'),
    url(r'^dummy/(?P<message>.+)/$', utils.dummy, name='dummy_extra'),

    # note: the following thing about static is only valid in dev.
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
