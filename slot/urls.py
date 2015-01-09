from django.conf.urls import patterns, url
import slot.views

urlpatterns = patterns(
    '',
    # url(r'^staff(?:/(P<uid>\d+))?/$', slot.views.staff_date, name='staff'),
    url(r'^staff(?:/(?P<uid>\d+))?/$', slot.views.staff_date, name='staff'),
    url(r'^staff(?:/(?P<uid>\d+))?/regular/$', slot.views.staff_regular, name='staff_regular'),

    # handle offer
    url(r'^(?P<uid>\d+)/offer/regular/add/$', slot.views.offer_regular_add, name='offer_regular_add'),
    url(r'^(?P<uid>\d+)/offer/regular/delete/$', slot.views.offer_regular_delete, name='offer_regular_delete'),
)

