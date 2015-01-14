from django.conf.urls import patterns, url

import slot.views

urlpatterns = patterns(
    '',
    # staff portal
    url(r'^staff(?:/(?P<uid>\d+))?/$', slot.views.day_staff, name='staff'),

    # classroom portal, classroom_id is required.
    url(r'^classroom/(?P<cid>\d+)/$', slot.views.day_classroom, name='classroom'),

    # assignment form
    url(r'^assign/(?P<need_id>\d+)/$', slot.views.assign, name='assign'),

    # handle offer (mostly for restful)
    url(r'^staff/(?P<uid>\d+)/offer/add/$', slot.views.offer_add, name='offer_add'),
    url(r'^staff/(?P<uid>\d+)/offer/delete/$', slot.views.offer_delete, name='offer_delete'),

    # handle need (mostly for restful)
    url(r'^classroom/(?P<cid>\d+)/need/add/$', slot.views.need_add, name='need_add'),
    url(r'^classroom/(?P<cid>\d+)/need/delete/$', slot.views.need_delete, name='need_delete'),
)


