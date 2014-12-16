from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^login/$', 'user.views.login', name='login'),
    url(r'^signup/$', 'user.views.signup', name='signup'),
)
