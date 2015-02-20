from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from log import views

urlpatterns = patterns(
    '',
    # staff portal
    url(r'^notification/$', views.notification, name='notification'),
    url(r'^mark_read/$', views.MarkRead.as_view(), name='mark_read'),

    url(r'^center/(?P<cid>[0-9]+)/comments/$', login_required(views.CommentByLocation.as_view()), name='comment_location'),
    url(r'^center/(?P<cid>[0-9]+)/comments/(?P<pk>[0-9]+)/$', views.CommentByLocationDetails.as_view(), name='comment_location_details'),
)
