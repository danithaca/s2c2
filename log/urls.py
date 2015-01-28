from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from log import views

urlpatterns = patterns(
    '',
    # staff portal
    url(r'^notification/$', views.notification, name='notification'),
    url(r'^mark_read/$', views.MarkRead.as_view(), name='mark_read'),
)
