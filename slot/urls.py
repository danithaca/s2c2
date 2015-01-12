from django.conf.urls import patterns, url
import slot.views

urlpatterns = patterns(
    '',
    # staff portal
    url(r'^staff(?:/(?P<uid>\d+))?/$', slot.views.staff_date, name='staff'),
    url(r'^staff(?:/(?P<uid>\d+))?/regular/$', slot.views.staff_regular, name='staff_regular'),

    # classroom portal
    url(r'^classroom/(?P<pk>\d+)/$', slot.views.classroom_date, name='classroom'),
    url(r'^classroom/(?P<pk>\d+)/regular/$', slot.views.classroom_regular, name='classroom_regular'),

    # assignment form
    url(r'^assign/(?P<need_id>\d+)/$', slot.views.assign_date, name='assign'),
    url(r'^assign/(?P<need_id>\d+)/regular$', slot.views.assign_regular, name='assign_regular'),

    # handle offer (mostly for restful)
    url(r'^(?P<uid>\d+)/offer/regular/add/$', slot.views.offer_regular_add, name='offer_regular_add'),
    url(r'^(?P<uid>\d+)/offer/regular/delete/$', slot.views.offer_regular_delete, name='offer_regular_delete'),

    # handle need (mostly for restful)
    url(r'^(?P<cid>\d+)/need/regular/add/$', slot.views.need_regular_add, name='need_regular_add'),
    url(r'^(?P<cid>\d+)/need/regular/delete/$', slot.views.need_regular_delete, name='need_regular_delete'),
)

