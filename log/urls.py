from django.conf.urls import patterns, url

import log.views

urlpatterns = patterns(
    '',
    # staff portal
    url(r'^notification/$', log.views.notification, name='notification'),
)
