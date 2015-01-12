from django.conf.urls import patterns, url
import slot.views

urlpatterns = patterns(
    '',
    # url(r'^staff(?:/(P<uid>\d+))?/$', slot.views.staff_date, name='staff'),
    url(r'^staff(?:/(?P<uid>\d+))?/$', slot.views.staff_date, name='staff'),
    url(r'^staff(?:/(?P<uid>\d+))?/regular/$', slot.views.staff_regular, name='staff_regular'),
    url(r'^classroom/(?P<pk>\d+)/$', slot.views.classroom_date, name='classroom'),
    url(r'^classroom/(?P<pk>\d+)/regular/$', slot.views.classroom_regular, name='classroom_regular'),

    # handle offer
    url(r'^(?P<uid>\d+)/offer/regular/add/$', slot.views.offer_regular_add, name='offer_regular_add'),
    url(r'^(?P<uid>\d+)/offer/regular/delete/$', slot.views.offer_regular_delete, name='offer_regular_delete'),

    # handle need
    url(r'^(?P<cid>\d+)/need/regular/add/$', slot.views.need_regular_add, name='need_regular_add'),
    url(r'^(?P<cid>\d+)/need/regular/delete/$', slot.views.need_regular_delete, name='need_regular_delete'),
)

