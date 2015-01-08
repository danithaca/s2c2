from django.conf.urls import patterns, url
import slot.views

urlpatterns = patterns(
    '',
    # url(r'^staff(?:/(P<uid>\d+))?/$', slot.views.staff_date, name='staff'),
    url(r'^staff(?:/(?P<uid>\d+))?/$', slot.views.staff_date, name='staff'),
    url(r'^staff(?:/(?P<uid>\d+))?/regular/$', slot.views.staff_regular, name='staff_regular'),
)

