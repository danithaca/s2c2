from django.conf.urls import patterns, url
from cal import views

urlpatterns = patterns(
    '',
    url(r'^staff(?:/(?P<uid>\d+))?/$', views.calendar_staff, name='staff'),
    url(r'^staff/(?P<uid>\d+)/events/$', views.calendar_staff_events, name='staff_events'),
    url(r'^staff/(?P<uid>\d+)/copy/$', views.calendar_staff_copy, name='staff_copy'),

    url(r'^classroom/(?P<cid>\d+)/$', views.calendar_classroom, name='classroom'),
    url(r'^classroom/(?P<cid>\d+)/events$', views.calendar_classroom_events, name='classroom_events'),
    url(r'^classroom/(?P<cid>\d+)/copy', views.calendar_classroom_copy, name='classroom_copy'),

    url(r'^classroom/(?P<cid>\d+)/assign$', views.assign, name='assign'),
    url(r'^classroom/(?P<cid>\d+)/delete$', views.need_delete_ajax, name='need_delete_ajax'),
)
