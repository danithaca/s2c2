from django.conf.urls import patterns, url

import user.views

urlpatterns = patterns(
    '',
    url(r'^$', user.views.profile, name='profile'),
    url(r'^(?P<uid>\d+)/$', user.views.profile, name='profile'),
    url(r'^login/$', user.views.login, name='login'),
    url(r'^logout/$', user.views.logout, name='logout'),
    url(r'^signup/$', user.views.signup, name='signup'),
    # url(r'^signup_simple/$', user.views.signup_simple, name='signup_simple'),
    url(r'^edit/$', user.views.edit, name='edit'),
    url(r'^picture/$', user.views.picture, name='picture'),

    url(r'^verify/$', user.views.verify, name='verify'),

    # url(r'^password/change/$', 'django.contrib.auth.views.password_change', {
    #     'template_name': 'user/password_change.html',
    #     'post_change_redirect': '/'
    # }, name='password_change'),

    # url(r'^password/reset/$', 'django.contrib.auth.views.password_reset', {
    #     'template_name': 'user/password_reset.html',
    #     'post_reset_redirect': reverse_lazy('user:login')
    # }, name='password_reset'),

    url(r'^password/change/$', user.views.password_change, name='password_change'),
    url(r'^password/reset/$', user.views.password_reset, name='password_reset'),
    url(r'^password/reset/(?P<uidb64>\w+)/(?P<token>[-\w]+)/$', user.views.password_reset_confirm, name='password_reset_confirm'),
)

