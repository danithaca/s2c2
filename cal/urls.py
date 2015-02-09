from django.conf.urls import patterns, url
from cal import views

urlpatterns = patterns(
    '',
    url(r'^staff(?:/(?P<uid>\d+))?/$', views.calendar_staff, name='staff'),
    url(r'^classroom/(?P<cid>\d+)/$', views.calendar_classroom, name='classroom'),
    url(r'^staff/(?P<uid>\d+)/events/$', views.calendar_staff_events, name='staff_events'),
)
