from django.conf.urls import patterns, url

from shout import views

urlpatterns = patterns(
    "",
    url(r'^add/$', views.ShoutToCircle.as_view(), name='add'),
    url(r'^contact/$', views.ShoutToAdmin.as_view(), name='contact'),
)
