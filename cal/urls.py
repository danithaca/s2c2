from django.conf.urls import patterns, url
from cal import views

urlpatterns = patterns(
    '',
    url(r'^staff(?:/(?P<uid>\d+))?/$', views.calendar_staff, name='staff'),
    url(r'^staff/(?P<uid>\d+)/events/$', views.calendar_staff_events, name='staff_events'),
    url(r'^staff/(?P<uid>\d+)/hours/$', views.calendar_staff_hours, name='staff_hours'),
    url(r'^staff/(?P<uid>\d+)/copy/$', views.calendar_staff_copy, name='staff_copy'),

    url(r'^classroom/(?P<cid>\d+)/$', views.calendar_classroom, name='classroom'),
    url(r'^classroom/(?P<cid>\d+)/events/$', views.calendar_classroom_events, name='classroom_events'),
    url(r'^classroom/(?P<cid>\d+)/copy/$', views.calendar_classroom_copy, name='classroom_copy'),
    url(r'^classroom/(?P<cid>\d+)/copy_day/$', views.calendar_classroom_copy_day, name='classroom_copy_day'),

    url(r'^classroom/(?P<cid>\d+)/assign/$', views.assign, name='assign'),
    url(r'^classroom/(?P<cid>\d+)/meet/$', views.meet, name='meet'),
    url(r'^classroom/(?P<cid>\d+)/user_autocomplete/$', views.classroom_user_autocomplete, name='user_autocomplete'),
    url(r'^classroom/(?P<cid>\d+)/delete/$', views.need_delete_ajax, name='need_delete_ajax'),

    url(r'^center/(?P<cid>\d+)/$', views.calendar_center, name='center'),
    url(r'^center/(?P<cid>\d+)/filled/$', views.calendar_center_events_filled, name='center_events_filled'),
    url(r'^center/(?P<cid>\d+)/empty/$', views.calendar_center_events_empty, name='center_events_empty'),
    url(r'^center/(?P<cid>\d+)/available/$', views.calendar_center_events_available, name='center_events_available'),
)
